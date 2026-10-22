# ------------------------------------------ #
# AI Knowledge Copilot - Logging Configuration #
# ------------------------------------------ #

"""
Structured logging configuration.

Uses JSON format for production environments.
Supports log rotation and configurable log levels.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config.settings import settings


def get_log_file_path() -> Path:
    """Get the log file path."""
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir / f"ai-knowledge-copilot-{settings.APP_ENVIRONMENT}.log"


def get_log_level() -> int:
    """Get log level from settings."""
    level_str = settings.APP_LOG_LEVEL.upper()
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    return levels.get(level_str, logging.INFO)


def json_formatter() -> logging.Formatter:
    """Create a JSON formatter for structured logs."""
    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_record = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "environment": settings.APP_ENVIRONMENT,
                "version": settings.BUILD_VERSION
            }
            
            # Add exception info if present
            if record.exc_info:
                log_record["exception"] = self.formatException(record.exc_info)
            
            # Add request info if available
            if hasattr(record, "request_id"):
                log_record["request_id"] = record.request_id
            if hasattr(record, "endpoint"):
                log_record["endpoint"] = record.endpoint
            if hasattr(record, "duration_ms"):
                log_record["duration_ms"] = record.duration_ms
            
            return str(log_record)
    
    return JsonFormatter(fmt="%(message)s")


def console_formatter() -> logging.Formatter:
    """Create a console formatter."""
    if settings.APP_ENVIRONMENT == "development":
        return logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        return logging.Formatter(
            "%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging() -> None:
    """Setup the root logging configuration."""
    root_logger = logging.getLogger()
    root_logger.setLevel(get_log_level())
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter())
    root_logger.addHandler(console_handler)
    
    # File handler (for production)
    if settings.APP_ENVIRONMENT != "development":
        log_file = get_log_file_path()
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(json_formatter())
        root_logger.addHandler(file_handler)
    
    # Suppress third-party logger noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    # Log startup info
    logger = logging.getLogger(__name__)
    logger.info("Logging configured", extra={
        "environment": settings.APP_ENVIRONMENT,
        "log_level": settings.APP_LOG_LEVEL
    })
