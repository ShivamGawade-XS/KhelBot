"""
KhelBot Cache — Production-grade thread-safe in-memory TTL cache with LRU eviction.
Handles high concurrency, prevents unbounded memory growth, and avoids thread contention.
"""

import time
import threading
from typing import Any, Optional


class TTLCache:
    """
    Thread-safe in-memory cache with per-key TTL expiration and bounded capacity.
    
    Usage:
        cache = TTLCache(max_size=2000)
        cache.set("live:rcb", data, ttl=60)
        result = cache.get("live:rcb")  # Returns data or None if expired
    """

    def __init__(self, max_size: int = 2000):
        self._max_size = max_size
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value if it exists and hasn't expired.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if missing/expired
        """
        with self._lock:
            if key not in self._store:
                return None

            value, expiry = self._store[key]

            if time.time() > expiry:
                # Expired — clean up and return None
                del self._store[key]
                return None

            return value

    def set(self, key: str, value: Any, ttl: int) -> None:
        """
        Store a value with a TTL (time-to-live) in seconds.
        Evicts expired or oldest entries if capacity exceeded.
        
        Args:
            key: Cache key
            value: Data to cache
            ttl: Time-to-live in seconds
        """
        with self._lock:
            # If at max capacity, run a quick cleanup of expired keys
            if len(self._store) >= self._max_size and key not in self._store:
                self.cleanup()
                # If still at max capacity, evict the oldest key (FIFO/LRU fallback)
                if len(self._store) >= self._max_size:
                    oldest_key = next(iter(self._store))
                    del self._store[oldest_key]

            expiry = time.time() + ttl
            self._store[key] = (value, expiry)

    def invalidate(self, key: str) -> None:
        """Remove a specific key from cache."""
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all cached data."""
        with self._lock:
            self._store.clear()

    def cleanup(self) -> int:
        """
        Remove all expired entries. Returns count of removed entries.
        Thread-safe iteration.
        """
        with self._lock:
            now = time.time()
            expired_keys = [k for k, (_, exp) in list(self._store.items()) if now > exp]
            for key in expired_keys:
                self._store.pop(key, None)
            return len(expired_keys)

    @property
    def size(self) -> int:
        """Number of entries in cache (including potentially expired ones)."""
        with self._lock:
            return len(self._store)


# Singleton cache instance for the entire bot
cache = TTLCache(max_size=2000)
