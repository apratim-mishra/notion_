import logging
import os
import sys

def setup_github_logging():
    """Set up logging configuration specifically for GitHub Actions."""
    # Check if running in GitHub Actions
    is_github = os.environ.get('GITHUB_ACTIONS') == 'true'
    
    log_level = logging.INFO
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with a higher log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    if is_github:
        # GitHub Actions-specific format that works well with the UI
        formatter = logging.Formatter('%(levelname)s - %(message)s')
    else:
        # Standard format for local development
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add formatter to handler
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    root_logger.addHandler(console_handler)
    
    return root_logger 