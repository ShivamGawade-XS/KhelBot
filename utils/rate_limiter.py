"""
KhelBot Rate Limiter — Per-user token bucket and sliding window rate limiting.
Protects upstream APIs (Groq, CricAPI, DuckDuckGo) from resource exhaustion attacks.
"""

import time
import threading
from typing import Tuple, Dict

# Global rate limit parameters
MAX_REQUESTS_PER_MINUTE = 15
WINDOW_SECONDS = 60
COOLDOWN_BETWEEN_COMMANDS_SEC = 1.5


class UserRateLimiter:
    """
    In-memory per-user sliding window rate limiter.
    Thread-safe and memory-bounded.
    """

    def __init__(self, max_requests: int = MAX_REQUESTS_PER_MINUTE, window_sec: int = WINDOW_SECONDS):
        self.max_requests = max_requests
        self.window_sec = window_sec
        self._user_history: Dict[int, list[float]] = {}
        self._lock = threading.RLock()

    def check(self, user_id: int) -> Tuple[bool, str]:
        """
        Check if user is within rate limits.
        
        Returns:
            (is_allowed, reason_message)
        """
        now = time.time()

        with self._lock:
            # Clean up old timestamps
            timestamps = self._user_history.get(user_id, [])
            valid_timestamps = [t for t in timestamps if now - t < self.window_sec]

            # Check rapid-fire cooldown (minimum time between consecutive requests)
            if valid_timestamps and (now - valid_timestamps[-1]) < COOLDOWN_BETWEEN_COMMANDS_SEC:
                return False, "⚡ Thoda sa break lo bhai! 1-2 second ruko aur phir try karo! 🏏"

            # Check window capacity
            if len(valid_timestamps) >= self.max_requests:
                oldest = valid_timestamps[0]
                wait_sec = int(self.window_sec - (now - oldest)) + 1
                return False, f"🚦 Thoda aaram se bhai! 1 minute ka limit cross ho gaya. {wait_sec} second ruko! ⏳"

            # Allow and append
            valid_timestamps.append(now)
            self._user_history[user_id] = valid_timestamps

            # Memory safeguard: evict inactive users periodically
            if len(self._user_history) > 5000:
                inactive = [uid for uid, t_list in self._user_history.items() if not t_list or (now - t_list[-1] > 300)]
                for uid in inactive:
                    self._user_history.pop(uid, None)

            return True, ""


# Singleton rate limiter
rate_limiter = UserRateLimiter()

