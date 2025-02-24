from loguru import logger
from typing import Optional

def get_logger(name: Optional[str] = None) -> logger:
    """Configure and return a logger instance"""
    # Remove default handler
    logger.remove()

    # Add a new handler with custom format
    logger.add(
        sink=lambda msg: print(msg),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
        enqueue=True
    )

    if name:
        return logger.bind(name=name)
    return logger