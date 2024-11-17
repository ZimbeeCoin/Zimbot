# src/__init__.py

"""
Root package for the Zimbot project.

This module serves as the main entry point for the project, maintaining
the authoritative version number, global configuration, and key project-level
constants.

Note: Core logging configuration is initialized through src/core/utils/logger.py.
"""

import logging
from typing import Any, Dict

# Version information
__version__ = "0.1.0"  # Format: major.minor.patch, following semantic versioning

# Initialize core logger for project-wide use
# Ensure this uses the logger configuration defined in src/core/utils/logger.py
try:
    from zimbot.core.utils.logger import configure_logger  # Ensure logger setup exists

    configure_logger()
    logger = logging.getLogger(__name__)
    logger.info("Zimbot project initialized with version %s", __version__)
except ImportError as e:
    print(f"Warning: Failed to configure project-wide logger: {e}")

# Expose version and logger for module-wide usage
__all__ = ["__version__", "logger"]

# Project-wide constants can be added here if needed
# For example, if you want to define an API timeout or other global settings,
# you could add them here, ensuring they don’t conflict with core or
# module-level configs.
