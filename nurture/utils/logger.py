"""
Simple Logger for Nurture Simulation
====================================

Basic logging functionality.
"""

import logging
from typing import Optional


class Logger:
    """Simple wrapper around Python logging."""
    
    def __init__(self, name: str, level: str = "INFO"):
        """Initialize logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)


def get_logger(name: str = "nurture", level: str = "INFO") -> Logger:
    """Get a logger instance."""
    return Logger(name, level)
