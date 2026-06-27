"""Logging utilities."""

import logging
import sys
from typing import Optional
from pathlib import Path
import os


def setup_logging(level: str = "INFO",
                  format_string: Optional[str] = None,
                  log_file: Optional[str] = None,
                  disable_file_logging: bool = False) -> None:
    """Setup logging configuration."""
    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if specified and not disabled
    if log_file and not disable_file_logging:
        log_path = Path(log_file)
        # Criar diretório de logs relativo ao projeto
        log_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except PermissionError:
            print(
                f"Warning: Could not create log file at {log_file}. Logging to console only.")

    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('pymongo').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for given name."""
    return logging.getLogger(name)


def initialize_logging(verbose: Optional[bool] = False, disable_file_logging: Optional[bool] = False):
    """Initializes logging configuration based on verbosity and file logging settings."""
    log_level = "DEBUG" if verbose else "INFO"

    disable_file_logging = disable_file_logging or os.getenv(
        "DISABLE_FILE_LOGGING", "false").lower() == "true"

    setup_logging(
        level=log_level,
        format_string="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        log_file="./logs/app.log" if not disable_file_logging else None,
        disable_file_logging=disable_file_logging
    )
