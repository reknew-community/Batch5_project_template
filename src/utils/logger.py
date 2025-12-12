"""Logging configuration."""

import logging
import sys
from pathlib import Path

from src.config.settings import settings


def setup_logging():
    """Set up logging configuration."""
    
    # Create logs directory
    logs_dir = settings.BASE_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logs_dir / "app.log"),
        ]
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
