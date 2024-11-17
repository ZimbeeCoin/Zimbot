# src/zimbot/core/integrations/email/email_service.py

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from zimbot.core.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

# Initialize settings
settings: Settings = get_settings()

# Initialize Jinja2 environment for email templates
env = Environment(
    loader=FileSystemLoader("src/zimbot/core/integrations/email/templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


class EmailService:
    def __init__(self) -> None:
        """
        Initialize the EmailService with SMTP configurations.
        """
        self.smtp_host = settings.smtp.host
        self.smtp_port = settings.smtp.port
        self.smtp_username = settings.smtp.username
        self.smtp_password = settings.smtp.password.get_secret_value()
        self.sender_email = settings.smtp.sender_email

    def _create_email_message(
        self,
        subject: str,
        recipient: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> MIMEMultipart:
        """
        Create an email message with both HTML and plain text content.

        Args:
            subject (str): The subject of the email.
            recipient (str): The recipient's email address.
            html_content (str): The HTML content of the email.
            text_content (Optional[str]): The plain text content of the email.

        Returns:
            MIMEMultipart: The constructed email message.
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = recipient

        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)

        part2 = MIMEText(html_content, "html")
        message.attach(part2)

        return message

    async def _send_email(
        self,
        subject: str,
        recipient: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> None:
        """
        Send an email using SMTP.

        Args:
            subject (str): The subject of the email.
            recipient (str): The recipient's email address.
            html_content (str): The HTML content of the email.
            text_content (Optional[str]): The plain text content of the email.

        Raises:
            Exception: If sending the email fails.
        """
        try:
            message = self._create_email_message(
                subject, recipient, html_content, text_content
            )

            with smtplib.SMTP(settings.smtp.host, settings.smtp.port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender_email, recipient, message.as_string())
                logger.info(f"Email sent to {recipient} with subject '{subject}'.")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            raise e

    async def send_mfa_setup_email(
        self, to_email: str, secret: str, otp_uri: str
    ) -> None:
        """
        Send MFA setup email with the secret key and OTP URI.

        Args:
            to_email (str): Recipient's email address.
            secret (str): MFA secret key.
            otp_uri (str): OTP URI for QR code generation.

        Raises:
            Exception: If sending the email fails.
        """
        try:
            subject = "Set Up Your Multi-Factor Authentication (MFA)"
            template = env.get_template("mfa_setup.html")
            html_content = template.render(secret=secret, otp_uri=otp_uri)
            text_content = f"Your MFA secret is {secret}. Use this to set up your authenticator app."

            await self._send_email(subject, to_email, html_content, text_content)
        except Exception as e:
            logger.error(f"Error sending MFA setup email to {to_email}: {e}")
            raise e

    async def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        """
        Send password reset email with the reset link.

        Args:
            to_email (str): Recipient's email address.
            reset_link (str): URL for password reset.

        Raises:
            Exception: If sending the email fails.
        """
        try:
            subject = "Password Reset Request"
            template = env.get_template("password_reset.html")
            html_content = template.render(reset_link=reset_link)
            text_content = (
                f"Use the following link to reset your password: {reset_link}"
            )

            await self._send_email(subject, to_email, html_content, text_content)
        except Exception as e:
            logger.error(f"Error sending password reset email to {to_email}: {e}")
            raise e

    async def send_password_reset_confirmation_email(self, to_email: str) -> None:
        """
        Send password reset confirmation email.

        Args:
            to_email (str): Recipient's email address.

        Raises:
            Exception: If sending the email fails.
        """
        try:
            subject = "Your Password Has Been Reset"
            template = env.get_template("password_reset_confirmation.html")
            html_content = template.render()
            text_content = "Your password has been successfully reset. If you did not perform this action, please contact support immediately."

            await self._send_email(subject, to_email, html_content, text_content)
        except Exception as e:
            logger.error(
                f"Error sending password reset confirmation email to {to_email}: {e}"
            )
            raise e
