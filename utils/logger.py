"""
KhelBot Logger — Structured logging with consistent formatting.
"""

import logging
import sys


def setup_logger(name: str = "khelbot", level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger with console output.
    
    Args:
        name: Logger name (default: 'khelbot')
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)

    # Console handler with formatted output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    formatter = logging.Formatter(
        fmt="%(asctime)s │ %(levelname)-8s │ %(name)-15s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Pre-configured logger for quick imports
log = setup_logger()
