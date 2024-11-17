# src/core/secrets/metrics_server.py

import logging
import threading
import time
from wsgiref.simple_server import WSGIRequestHandler, make_server

from prometheus_client import make_wsgi_app

logger = logging.getLogger(__name__)


class RateLimitedHandler(WSGIRequestHandler):
    """
    Custom WSGIRequestHandler with simple rate limiting to prevent overwhelming the metrics server.
    """

    rate_limit_lock = threading.Lock()
    last_request_time = 0
    # Minimum interval between requests in seconds (e.g., 10 requests per second)
    min_interval = 0.1

    def handle(self):
        with self.rate_limit_lock:
            current_time = time.time()
            if current_time - self.last_request_time < self.min_interval:
                # Too soon since last request; send 429 Too Many Requests
                self.send_response(429)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"429 Too Many Requests")
                logger.warning(f"Rate limit exceeded from {self.client_address}")
                return
            self.last_request_time = current_time
        super().handle()


class MetricsServer:
    """
    Metrics server that exposes Prometheus metrics with enhanced error handling and resource optimization.
    """

    def __init__(self, port: int = 8000):
        """
        Initialize the MetricsServer.

        Args:
            port (int): The port number to serve metrics on.
        """
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        """
        Start the metrics server.
        """
        try:
            app = make_wsgi_app()
            self.server = make_server(
                "", self.port, app, handler_class=RateLimitedHandler
            )
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            logger.info(f"Prometheus metrics server started on port {self.port}.")
        except Exception as e:
            logger.error(
                f"Failed to start Prometheus metrics server: {e}", exc_info=True
            )
            raise

    def stop(self):
        """
        Stop the metrics server.
        """
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
                self.thread.join(timeout=5)
                logger.info("Prometheus metrics server stopped.")
            except Exception as e:
                logger.error(
                    f"Failed to stop Prometheus metrics server: {e}", exc_info=True
                )
        else:
            logger.warning("Metrics server was not running.")

    def __enter__(self):
        """
        Context manager entry; starts the server.
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit; stops the server.
        """
        self.stop()
        if exc_type:
            logger.error(
                "Exception occurred in MetricsServer context.",
                exc_info=(exc_type, exc_val, exc_tb),
            )
