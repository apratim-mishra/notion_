import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_to_file=False, log_level=logging.INFO):
    """Configure logging for the application.
    
    Args:
        log_to_file: Whether to log to a file in addition to console
        log_level: The logging level to use
    
    Returns:
        Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_to_file and not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        file_handler = RotatingFileHandler(
            "logs/notion_search.log", 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logging.getLogger(__name__)