"""
Unit tests for the safe_reply chunking and utility functions.
"""

import pytest
from utils.reply import _split_text


def test_split_text_short():
    text = "Short message under 4000 characters."
    chunks = _split_text(text, max_length=100)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_split_text_long_with_newlines():
    line1 = "Line one of content.\n" * 10
    line2 = "Line two of content.\n" * 10
    text = line1 + line2
    chunks = _split_text(text, max_length=len(line1) + 10)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= len(line1) + 10


def test_split_text_unbroken_string():
    text = "A" * 500
    chunks = _split_text(text, max_length=200)
    assert len(chunks) == 3
    assert chunks[0] == "A" * 200
    assert chunks[1] == "A" * 200
    assert chunks[2] == "A" * 100

