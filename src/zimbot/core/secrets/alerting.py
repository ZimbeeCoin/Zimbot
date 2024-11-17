# src/core/secrets/alerting.py

import asyncio
import logging
import smtplib
import time
from collections import deque
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)

# Constants for batching
BATCH_THRESHOLD = 10  # Number of alerts before sending a batch
BATCH_INTERVAL = 60  # Time interval in seconds to send batches

# Constants for rate-limiting
MAX_ALERTS_PER_MINUTE = 5  # Maximum number of alerts that can be sent per minute


class Alerting:
    """
    Alerting utility for sending alerts via email, Slack, or generic webhooks.
    Implements connection pooling, batching, and rate-limiting for efficiency.
    """

    def __init__(
        self,
        email_alerts: List[str],
        slack_webhooks: List[str],
        webhook_urls: List[str],
        smtp_config: Dict[str, Any],
    ):
        """
        Initialize the Alerting utility.

        Args:
            email_alerts (List[str]): List of email addresses to send alerts to.
            slack_webhooks (List[str]): List of Slack webhook URLs.
            webhook_urls (List[str]): List of generic webhook URLs.
            smtp_config (Dict[str, Any]): SMTP configuration for sending emails.
        """
        self.email_alerts = email_alerts
        self.slack_webhooks = slack_webhooks
        self.webhook_urls = webhook_urls
        self.smtp_config = smtp_config

        # Initialize aiohttp session for webhooks
        self.session = aiohttp.ClientSession()

        # Initialize SMTP connection pool if possible
        self.smtp_lock = asyncio.Lock()
        self.smtp_server: Optional[smtplib.SMTP] = None
        self._initialize_smtp_pool()

        # Initialize alert batching
        self.alert_queue = deque()
        self.batch_task = asyncio.create_task(self._batch_alerts())

        # Rate-limiting variables
        self.alerts_sent_in_current_window = 0
        self.rate_limit_lock = asyncio.Lock()
        self.rate_limit_reset_time = time.time() + 60  # Reset every minute

    def _initialize_smtp_pool(self):
        """
        Initialize SMTP connection pool.
        """
        try:
            server = smtplib.SMTP(
                self.smtp_config["hostname"], self.smtp_config["port"]
            )
            if self.smtp_config.get("start_tls", True):
                server.starttls()
            server.login(self.smtp_config["username"], self.smtp_config["password"])
            self.smtp_server = server
            logger.debug("SMTP connection pool initialized successfully.")
        except Exception as e:
            logger.error(
                f"Failed to initialize SMTP connection pool: {e}", exc_info=True
            )

    async def send_alert(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Send an alert through all configured channels with batching and rate-limiting.

        Args:
            message (str): The alert message.
            metadata (Optional[Dict[str, Any]]): Additional metadata for the alert.
        """
        full_message = message
        if metadata:
            full_message += f"\nMetadata: {metadata}"
        self.alert_queue.append(full_message)

        # Check rate limit before flushing alerts
        async with self.rate_limit_lock:
            current_time = time.time()
            if current_time >= self.rate_limit_reset_time:
                # Reset rate limit counters
                self.alerts_sent_in_current_window = 0
                self.rate_limit_reset_time = current_time + 60

            if self.alerts_sent_in_current_window < MAX_ALERTS_PER_MINUTE:
                if len(self.alert_queue) >= BATCH_THRESHOLD:
                    await self._flush_alerts()
            else:
                logger.warning("Rate limit exceeded, alert not sent.")

    async def _flush_alerts(self):
        """
        Flush the alert queue by sending all accumulated alerts.
        """
        if not self.alert_queue:
            return

        async with self.rate_limit_lock:
            current_time = time.time()
            if current_time >= self.rate_limit_reset_time:
                # Reset rate limit counters
                self.alerts_sent_in_current_window = 0
                self.rate_limit_reset_time = current_time + 60

            if self.alerts_sent_in_current_window >= MAX_ALERTS_PER_MINUTE:
                logger.warning("Rate limit exceeded, alerts not sent.")
                return

            # Prepare batch messages
            batch_size = min(
                MAX_ALERTS_PER_MINUTE - self.alerts_sent_in_current_window,
                len(self.alert_queue),
            )
            batch_messages = "\n---\n".join(
                [self.alert_queue.popleft() for _ in range(batch_size)]
            )

            # Send alerts
            tasks = []
            if self.email_alerts:
                tasks.append(self._send_email(batch_messages))
            if self.slack_webhooks:
                tasks.append(self._send_slack(batch_messages))
            if self.webhook_urls:
                tasks.append(self._send_generic_webhook(batch_messages))

            await asyncio.gather(*tasks)

            self.alerts_sent_in_current_window += 1

    async def _batch_alerts(self):
        """
        Periodically flush alerts based on BATCH_INTERVAL.
        """
        try:
            while True:
                await asyncio.sleep(BATCH_INTERVAL)
                await self._flush_alerts()
        except asyncio.CancelledError:
            # Task was cancelled, exit gracefully
            pass

    async def _send_email(self, message: str):
        """
        Send an email alert.

        Args:
            message (str): The alert message.
        """
        if not self.email_alerts or not self.smtp_server:
            return
        try:
            msg = MIMEText(message)
            msg["Subject"] = "SecretsManager Alert"
            msg["From"] = self.smtp_config["from_email"]
            msg["To"] = ", ".join(self.email_alerts)

            async with self.smtp_lock:
                self.smtp_server.sendmail(
                    self.smtp_config["from_email"], self.email_alerts, msg.as_string()
                )
            logger.debug("Email alert sent successfully.")
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error while sending email alert: {e}", exc_info=True)
        except Exception as e:
            logger.error(
                f"Unexpected error while sending email alert: {e}", exc_info=True
            )

    async def _send_slack(self, message: str):
        """
        Send a Slack alert.

        Args:
            message (str): The alert message.
        """
        if not self.slack_webhooks:
            return
        for webhook in self.slack_webhooks:
            try:
                payload = {"text": message}
                async with self.session.post(webhook, json=payload) as resp:
                    response_text = await resp.text()
                    if resp.status != 200:
                        logger.error(
                            f"Failed to send Slack alert to {webhook}: {resp.status} {response_text}"
                        )
            except aiohttp.ClientError as e:
                logger.error(
                    f"Client error while sending Slack alert to {webhook}: {e}",
                    exc_info=True,
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error while sending Slack alert to {webhook}: {e}",
                    exc_info=True,
                )

    async def _send_generic_webhook(self, message: str):
        """
        Send a generic webhook alert.

        Args:
            message (str): The alert message.
        """
        if not self.webhook_urls:
            return
        for webhook in self.webhook_urls:
            try:
                payload = {"message": message}
                async with self.session.post(webhook, json=payload) as resp:
                    response_text = await resp.text()
                    if resp.status != 200:
                        logger.error(
                            f"Failed to send webhook alert to {webhook}: {resp.status} {response_text}"
                        )
            except aiohttp.ClientError as e:
                logger.error(
                    f"Client error while sending webhook alert to {webhook}: {e}",
                    exc_info=True,
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error while sending webhook alert to {webhook}: {e}",
                    exc_info=True,
                )

    async def close(self):
        """
        Gracefully close all connections and tasks.
        """
        try:
            await self._flush_alerts()
        finally:
            if self.smtp_server:
                try:
                    self.smtp_server.quit()
                    logger.debug("SMTP connection pool closed.")
                except Exception as e:
                    logger.error(
                        f"Failed to close SMTP connection pool: {e}", exc_info=True
                    )

            await self.session.close()

            # Cancel the batch task and wait for it to finish
            if self.batch_task:
                self.batch_task.cancel()
                try:
                    await self.batch_task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(
                        f"Error while cancelling batch task: {e}", exc_info=True
                    )
            logger.debug("Alerting utility shutdown completed.")
