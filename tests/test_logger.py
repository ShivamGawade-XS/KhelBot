"""
Unit tests for logger sensitive data redaction.
"""

import logging
from utils.logger import SensitiveDataFilter


def test_sensitive_data_filter_redacts_tokens():
    filter_instance = SensitiveDataFilter()
    
    # Telegram Bot Token
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="test.py", lineno=1,
        msg="Bot initialized with token 123456789:ABCdefGHIjklMNOpqrSTUvwxYZ123456789 successfully",
        args=(), exc_info=None
    )
    filter_instance.filter(record)
    assert "[REDACTED_SECRET]" in record.msg
    assert "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ123456789" not in record.msg


def test_sensitive_data_filter_masks_telegram_user_id():
    filter_instance = SensitiveDataFilter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="test.py", lineno=1,
        msg="Command received from 987654321 in chat",
        args=(), exc_info=None
    )
    filter_instance.filter(record)
    assert "987***321" in record.msg
    assert "987654321" not in record.msg

