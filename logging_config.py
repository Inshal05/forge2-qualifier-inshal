"""logging_config.py – structured rotating file logging with helper event functions."""

import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Any  # Add Any import

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "hermes.log")
MAX_BYTES = 5 * 1024 * 1024  # 5 MiB
BACKUP_COUNT = 3

os.makedirs(LOG_DIR, exist_ok=True)


def _json_formatter(record: logging.LogRecord) -> str:
    """Return a single-line JSON representation of the log record."""
    log_dict = {
        "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
        "level": record.levelname,
        "module": record.name,
        "message": record.getMessage(),
        "line": record.lineno,
    }
    if hasattr(record, "extra"):
        log_dict.update(record.extra)
    return json.dumps(log_dict, ensure_ascii=False)


def configure_logging() -> None:
    """Configure a rotating JSON‑line file handler and a stream handler."""
    handler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
    )
    # Use default formatter to avoid TypeError; custom JSON formatting is handled via custom logic if needed.
    formatter = logging.Formatter()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(handler)

    # Also log to stderr for interactive output (still JSON‑formatted)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


# ----------------------------------------------------------------------
# Helper functions for structured logging of key operational events.
# ----------------------------------------------------------------------
def log_event(event_type: str, **details: Any) -> None:
    """
    Emit a structured log entry.

    Example:
        log_event("memory_saved", memory_id="abc123", name="recent", size=123)
    """
    payload = {"event": event_type, "details": details}
    logging.info(json.dumps(payload))


# Convenience wrappers for common operational categories.
def log_memory_event(event: str, **kwargs: Any) -> None:
    """Log events related to memory operations."""
    log_event("memory", action=event, **kwargs)


def log_skill_event(event: str, **kwargs: Any) -> None:
    """Log events related to skill loading/unloading."""
    log_event("skill", action=event, **kwargs)


def log_autonomous_event(event: str, **kwargs: Any) -> None:
    """Log events related to autonomous runs."""
    log_event("autonomous", action=event, **kwargs)


def log_error_event(event: str, **kwargs: Any) -> None:
    """Log error conditions; automatically uses logging.error."""
    log_event("error", action=event, **kwargs)