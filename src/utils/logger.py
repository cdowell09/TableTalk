import sys

from loguru import logger


def setup_logger(
    name: str | None = None,
    level: str | int = "DEBUG",
    format_string: str | None = None,
    **kwargs: dict,
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
        sink=sys.stderr, format=format_string, level=level, enqueue=True, **kwargs
    )

    if name:
        return logger.bind(name=name)
    return logger


def get_logger(name: str | None = None) -> logger:
    """Get a configured logger instance"""
    return setup_logger(name=name)
