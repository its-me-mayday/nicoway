from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Any

_buffer: deque[dict[str, Any]] = deque(maxlen=300)
_lock = threading.Lock()

LEVEL_LABELS = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARNING: "WARN",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRIT",
}

# Loggers too noisy to show in the UI
_SKIP_LOGGERS = {
    "uvicorn.access",
    "httpx",
    "httpcore",
    "apscheduler.executors.default",
}


class UILogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        if record.name in _SKIP_LOGGERS:
            return
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        entry = {
            "t": round(time.time() * 1000),  # ms epoch
            "level": LEVEL_LABELS.get(record.levelno, "LOG"),
            "logger": record.name.split(".")[-1],  # last segment only
            "msg": msg,
        }
        with _lock:
            _buffer.append(entry)


def get_entries(since_ms: int = 0) -> list[dict[str, Any]]:
    with _lock:
        return [e for e in _buffer if e["t"] > since_ms]


def install(root_logger: logging.Logger) -> None:
    handler = UILogHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(handler)
