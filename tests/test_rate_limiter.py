"""
Unit tests for the rate limiter.
"""

import time
import pytest
from utils.rate_limiter import UserRateLimiter


def test_rate_limiter_allows_initial():
    limiter = UserRateLimiter(max_requests=5, window_sec=10)
    allowed, msg = limiter.check(user_id=101)
    assert allowed is True
    assert msg == ""


def test_rate_limiter_rapid_fire():
    limiter = UserRateLimiter(max_requests=5, window_sec=10)
    allowed1, _ = limiter.check(user_id=102)
    assert allowed1 is True
    
    # Immediate second call should be caught by rapid fire cooldown (<1.5s)
    allowed2, msg2 = limiter.check(user_id=102)
    assert allowed2 is False
    assert "break" in msg2.lower()


def test_rate_limiter_window_capacity():
    limiter = UserRateLimiter(max_requests=3, window_sec=10)
    now = time.time()
    # Spaced out more than 1.5s so cooldown passes, but inside 10s window
    limiter._user_history[103] = [now - 6.0, now - 4.0, now - 2.0]
    
    allowed, msg = limiter.check(user_id=103)
    assert allowed is False
    assert "limit" in msg.lower()
