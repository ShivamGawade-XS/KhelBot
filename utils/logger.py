"""
KhelBot Logger — Structured logging with PII/secret scrubbing and compliance filters.
"""

import re
import logging
import sys


class SensitiveDataFilter(logging.Filter):
    """Filter that masks API keys, secrets, and raw Telegram user IDs in log records."""

    # Matches common secret formats (e.g. Bot tokens, Groq keys, Supabase secrets)
    SECRET_PATTERNS = [
        re.compile(r'\b\d{9,10}:[A-Za-z0-9_-]{35}\b'),  # Telegram Bot Token
        re.compile(r'gsk_[A-Za-z0-9]{40,}'),           # Groq API Key
        re.compile(r'sb_secret_[A-Za-z0-9_-]{20,}'),   # Supabase Secret Key
    ]

    USER_ID_PATTERN = re.compile(r'\b(from|user|uid)[:=\s]+(\d{6,12})\b', re.IGNORECASE)

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern in self.SECRET_PATTERNS:
                record.msg = pattern.sub("[REDACTED_SECRET]", record.msg)
            
            # Mask user IDs: e.g. "from 123456789" -> "from 123***789"
            def _mask_uid(match):
                prefix = match.group(1)
                uid_str = match.group(2)
                masked = f"{uid_str[:3]}***{uid_str[-3:]}" if len(uid_str) >= 6 else "***"
                return f"{prefix} {masked}"

            record.msg = self.USER_ID_PATTERN.sub(_mask_uid, record.msg)

        return True


def setup_logger(name: str = "khelbot", level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a structured logger with PII scrubbing.
    
    Args:
        name: Logger name (default: 'khelbot')
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    formatter = logging.Formatter(
        fmt="%(asctime)s │ %(levelname)-8s │ %(name)-15s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)

    return logger


# Pre-configured logger for quick imports
log = setup_logger()
