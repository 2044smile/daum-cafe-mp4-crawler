"""Logging utilities (currently using print, can be extended)"""
import logging
from config.settings import LogConfig


def setup_logger(name='daum-cafe-crawler'):
    """
    Setup logger with configuration
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LogConfig.LOG_LEVEL))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LogConfig.LOG_LEVEL))
    
    # Formatter
    formatter = logging.Formatter(LogConfig.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if LogConfig.SAVE_TO_FILE:
        LogConfig.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LogConfig.LOG_FILE)
        file_handler.setLevel(getattr(logging, LogConfig.LOG_LEVEL))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
