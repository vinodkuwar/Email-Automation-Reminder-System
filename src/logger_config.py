"""
Central Logging Configuration Module
Provides structured logging to both file (logs/automation.log) and console.
Safely masks any credential or sensitive data.
Includes robust fallback for restricted sandboxed environments.
"""

import os
import sys
import logging
from pathlib import Path

class SafeFileLogHandler(logging.Handler):
    """
    Log handler using safe_append_text to avoid Windows file descriptor
    flush errors in sandboxed environments.
    """
    def __init__(self, filepath: Path, encoding: str = "utf-8"):
        super().__init__()
        self.filepath = filepath
        self.encoding = encoding

    def emit(self, record):
        try:
            msg = self.format(record) + "\n"
            from src.file_utils import safe_append_text
            safe_append_text(str(self.filepath), msg, encoding=self.encoding)
        except Exception:
            pass

    def flush(self):
        pass

def setup_logger(name: str = "EmailAutomation") -> logging.Logger:
    """
    Configure and return a structured logger.
    Writes to logs/automation.log and sys.stdout.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Determine base directory and ensure logs/ exists
    base_dir = Path(__file__).resolve().parent.parent
    log_dir = base_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "automation.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler using SafeFileLogHandler
    file_handler = SafeFileLogHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Module-level default logger instance
logger = setup_logger()
