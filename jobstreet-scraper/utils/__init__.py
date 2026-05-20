"""
Utility functions for the JobStreet scraper.
Includes logging, file handling, and helper functions.
"""

import sys
import os
from pathlib import Path
from loguru import logger as loguru_logger


def get_logger(name: str):
    """
    Get configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured loguru logger
    """
    # Remove default handler
    loguru_logger.remove()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Add file handler
    loguru_logger.add(
        log_dir / "scraper.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="500 MB",
        retention="7 days",
    )
    
    # Add console handler
    loguru_logger.add(
        sys.stdout,
        level="INFO",
        format="<level>{time:HH:mm:ss}</level> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    )
    
    return loguru_logger.bind(name=name)


def ensure_directory(path: str) -> None:
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)
