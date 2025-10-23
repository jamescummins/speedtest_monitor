"""
Logging configuration for the Speedtest Monitor application
"""

import logging
import sys
import os
from config import DATA_DIR, LOG_FILE, DEBUG_MODE


def setup_logging():
    """Configure logging to file and console"""
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    # Set log level based on debug mode
    log_level = logging.DEBUG if DEBUG_MODE else logging.INFO
    
    # Configure logging with both file and console handlers
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log initial setup information
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    logger.info(f"Log file: {LOG_FILE}")
    
    return logger


def get_logger(name=None):
    """Get a logger instance for a specific module"""
    return logging.getLogger(name or __name__)