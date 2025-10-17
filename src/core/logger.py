"""
Logging configuration for MaxManager
Provides centralized logging with different levels and outputs
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging(
    level: int = logging.DEBUG,
    log_file: Optional[str] = None,
    console_output: bool = True,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 5
) -> None:
    """
    Setup logging configuration for MaxManager
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        console_output: Enable console output
    """
    
    # Create logs directory if needed
    if log_file is None:
        log_dir = Path.home() / ".maxmanager" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        # Single file logging (append): keep one file maxmanager.log
        log_file = log_dir / "maxmanager.log"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler: single file, append mode
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"MaxManager logging initialized - Level: {logging.getLevelName(level)}")
    logger.info(f"Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance for a module
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class MaxManagerLogger:
    """
    Custom logger class with MaxManager-specific features
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with additional context"""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | {context}"
        return message
    
    def log_user_action(self, action: str, **kwargs) -> None:
        """Log user action for analytics/debugging"""
        self.info(f"USER_ACTION: {action}", **kwargs)
    
    def log_module_event(self, module: str, event: str, **kwargs) -> None:
        """Log module-specific event"""
        self.info(f"MODULE_EVENT: {module}.{event}", **kwargs)
    
    def log_performance(self, operation: str, duration: float, **kwargs) -> None:
        """Log performance metrics"""
        self.info(f"PERFORMANCE: {operation} took {duration:.3f}s", **kwargs)