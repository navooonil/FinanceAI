import json
import logging
import logging.config
import sys
from datetime import datetime
from typing import Any, Dict

from app.config import settings


class JSONFormatter(logging.Formatter):
    """
    Custom logging formatter that outputs JSON strings.
    Fits production log aggregation systems (e.g. Datadog, ELK, CloudWatch).
    """

    def format(self, record: logging.LogRecord) -> str:
        # Construct log details
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "environment": settings.ENVIRONMENT,
        }

        # Include exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include extra attributes supplied via extra={}
        # Skip standard LogRecord attributes
        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message"
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs:
                log_data[key] = value

        return json.dumps(log_data)


def setup_logging() -> None:
    """
    Initializes the logging system with standard configurations.
    Uses JSON formatting for non-development environments, and readable standard formats
    for development to ensure excellent developer ergonomics.
    """
    log_level = "DEBUG" if settings.ENVIRONMENT == "development" else "INFO"

    # Define logging handlers and formatters
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "console": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "stdout_handler": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "console" if settings.ENVIRONMENT == "development" else "json",
                "level": log_level,
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["stdout_handler"],
                "level": log_level,
                "propagate": True,
            },
            "uvicorn": {
                "handlers": ["stdout_handler"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["stdout_handler"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["stdout_handler"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["stdout_handler"],
                "level": "WARNING",  # Set to INFO to log all SQL statements in dev
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)
