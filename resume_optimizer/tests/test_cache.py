"""
Tests for the cache module.
"""

import unittest
import time
from resume_optimizer.cache import Cache, generate_cache_key


class TestCache(unittest.TestCase):
    """Test cases for the cache module."""

    def test_cache_set_get(self):
        """Test basic cache set and get operations."""
        cache = Cache()
        cache.set("test_key", "test_value", 60)
        self.assertEqual(cache.get("test_key"), "test_value")

    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = Cache()
        self.assertIsNone(cache.get("non_existent_key"))

    def test_cache_ttl_expiry(self):
        """Test cache TTL expiration."""
        cache = Cache()
        # Set with a very short TTL
        cache.set("short_lived", "value", 1)
        # Verify it exists initially
        self.assertEqual(cache.get("short_lived"), "value")
        # Wait for expiration
        time.sleep(1.1)
        # Verify it's gone after expiration
        self.assertIsNone(cache.get("short_lived"))

    def test_cache_clear(self):
        """Test clearing the cache."""
        cache = Cache()
        cache.set("key1", "value1", 60)
        cache.set("key2", "value2", 60)
        cache.clear()
        self.assertIsNone(cache.get("key1"))
        self.assertIsNone(cache.get("key2"))

    def test_remove_expired(self):
        """Test removing expired entries."""
        cache = Cache()
        # Add entries with different TTLs
        cache.set("expired1", "value1", 1)
        cache.set("expired2", "value2", 1)
        cache.set("fresh", "value3", 60)
        
        # Wait for some entries to expire
        time.sleep(1.1)
        
        # Remove expired entries and verify count
        removed = cache.remove_expired()
        self.assertEqual(removed, 2)
        
        # Verify expired entries are gone
        self.assertIsNone(cache.get("expired1"))
        self.assertIsNone(cache.get("expired2"))
        
        # Verify fresh entry remains
        self.assertEqual(cache.get("fresh"), "value3")

    def test_generate_cache_key(self):
        """Test generating cache keys."""
        # Same inputs should generate the same key
        key1 = generate_cache_key("resume", "job")
        key2 = generate_cache_key("resume", "job")
        self.assertEqual(key1, key2)
        
        # Different inputs should generate different keys
        key3 = generate_cache_key("different", "job")
        self.assertNotEqual(key1, key3)


if __name__ == "__main__":
    unittest.main()
