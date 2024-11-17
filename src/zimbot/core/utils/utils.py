import logging
from typing import Optional


def setup_logger(name: str, level: Optional[int] = logging.INFO) -> logging.Logger:
    """Set up a logger with the specified name and level."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
