"""Main application entry point."""

import logging
import sys
from pathlib import Path

# Add src to path for development
sys.path.append(str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def main():
    """Main application function."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")
    
    # Your application logic here
    print(f"🚀 {settings.APP_NAME} is running!")
    print(f"Environment: {settings.APP_ENV}")
    print(f"Debug mode: {settings.DEBUG}")
    
    # Example: Start web server if this is a web application
    if hasattr(settings, 'PORT'):
        print(f"Server would start on port {settings.PORT}")


if __name__ == "__main__":
    main()
