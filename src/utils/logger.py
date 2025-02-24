import sys
from loguru import logger
from typing import Optional, Union, Dict

def setup_logger(
    name: Optional[str] = None,
    level: Union[str, int] = "DEBUG",
    format_string: Optional[str] = None,
    **kwargs: Dict
) -> logger:
    """Configure and return a logger instance with custom settings"""
    # Remove default handler
    logger.remove()

    # Default format if none provided
    if not format_string:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

    # Add a new handler with custom format
    logger.add(
        sink=sys.stderr,
        format=format_string,
        level=level,
        enqueue=True,
        **kwargs
    )

    if name:
        return logger.bind(name=name)
    return logger

def get_logger(name: Optional[str] = None) -> logger:
    """Get a configured logger instance"""
    return setup_logger(name=name)