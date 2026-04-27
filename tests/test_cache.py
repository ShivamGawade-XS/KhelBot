"""
Tests for KhelBot cache service — verifies TTL behavior and cache operations.
"""

import time
import pytest
from services.cache import TTLCache


class TestTTLCache:
    """Tests for TTLCache."""

    def setup_method(self):
        """Create a fresh cache for each test."""
        self.cache = TTLCache()

    def test_set_and_get(self):
        self.cache.set("key1", "value1", ttl=60)
        assert self.cache.get("key1") == "value1"

    def test_missing_key(self):
        assert self.cache.get("nonexistent") is None

    def test_expired_key(self):
        self.cache.set("key1", "value1", ttl=0)  # Expires immediately
        time.sleep(0.01)
        assert self.cache.get("key1") is None

    def test_invalidate(self):
        self.cache.set("key1", "value1", ttl=60)
        self.cache.invalidate("key1")
        assert self.cache.get("key1") is None

    def test_invalidate_nonexistent(self):
        # Should not raise
        self.cache.invalidate("nonexistent")

    def test_clear(self):
        self.cache.set("key1", "value1", ttl=60)
        self.cache.set("key2", "value2", ttl=60)
        self.cache.clear()
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None
        assert self.cache.size == 0

    def test_overwrite(self):
        self.cache.set("key1", "old", ttl=60)
        self.cache.set("key1", "new", ttl=60)
        assert self.cache.get("key1") == "new"

    def test_size(self):
        assert self.cache.size == 0
        self.cache.set("key1", "value1", ttl=60)
        assert self.cache.size == 1
        self.cache.set("key2", "value2", ttl=60)
        assert self.cache.size == 2

    def test_cleanup(self):
        self.cache.set("fresh", "data", ttl=60)
        self.cache.set("stale", "data", ttl=0)
        time.sleep(0.01)
        removed = self.cache.cleanup()
        assert removed == 1
        assert self.cache.get("fresh") == "data"
        assert self.cache.get("stale") is None

    def test_complex_values(self):
        """Cache should handle dicts, lists, and nested structures."""
        data = {"teams": ["CSK", "MI"], "score": {"runs": 185, "wickets": 6}}
        self.cache.set("match", data, ttl=60)
        assert self.cache.get("match") == data
