"""
Logging configuration for MaxManager
Provides centralized logging with different levels and outputs
"""

import logging
import sys
from pathlib import Path
from typing import Optional


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
    return logging.getLogger(name)
