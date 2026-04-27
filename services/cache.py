"""
KhelBot Cache — Lightweight in-memory TTL cache.
No Redis needed — sufficient for <100 concurrent users with ephemeral sports data.
"""

import time
from typing import Any, Optional


class TTLCache:
    """
    Simple in-memory cache with per-key TTL expiration.
    
    Usage:
        cache = TTLCache()
        cache.set("live:rcb", data, ttl=60)
        result = cache.get("live:rcb")  # Returns data or None if expired
    """

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value if it exists and hasn't expired.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if missing/expired
        """
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
        
        Args:
            key: Cache key
            value: Data to cache
            ttl: Time-to-live in seconds
        """
        expiry = time.time() + ttl
        self._store[key] = (value, expiry)

    def invalidate(self, key: str) -> None:
        """Remove a specific key from cache."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all cached data."""
        self._store.clear()

    def cleanup(self) -> int:
        """
        Remove all expired entries. Returns count of removed entries.
        Call periodically if memory is a concern.
        """
        now = time.time()
        expired_keys = [k for k, (_, exp) in self._store.items() if now > exp]
        for key in expired_keys:
            del self._store[key]
        return len(expired_keys)

    @property
    def size(self) -> int:
        """Number of entries in cache (including potentially expired ones)."""
        return len(self._store)


# Singleton cache instance for the entire bot
cache = TTLCache()
