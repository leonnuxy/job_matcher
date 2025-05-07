"""
Cache module for resume optimization.

Provides a simple in-memory cache that can be extended to use external caching systems.
"""

import time
import hashlib
from typing import Dict, Any, Optional, Tuple


class Cache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        """Initialize an empty cache."""
        self._cache: Dict[str, Tuple[Any, float]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache if it exists and hasn't expired.
        
        Args:
            key (str): The cache key to retrieve.
            
        Returns:
            Optional[Any]: The cached value if found and not expired, None otherwise.
        """
        if key not in self._cache:
            return None
        
        value, expiry_time = self._cache[key]
        current_time = time.time()
        
        # Check if the entry has expired
        if current_time > expiry_time:
            # Remove expired entry
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """
        Store a value in the cache with a specified TTL.
        
        Args:
            key (str): The cache key.
            value (Any): The value to store.
            ttl_seconds (int): Time-to-live in seconds.
        """
        expiry_time = time.time() + ttl_seconds
        self._cache[key] = (value, expiry_time)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
    
    def remove_expired(self) -> int:
        """
        Remove all expired cache entries.
        
        Returns:
            int: Number of expired entries removed.
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry_time) in self._cache.items()
            if current_time > expiry_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)


# Global instance for simple use cases
_default_cache = Cache()

def get_default_cache() -> Cache:
    """
    Get the default global cache instance.
    
    Returns:
        Cache: The default cache instance.
    """
    return _default_cache

def generate_cache_key(resume_text: str, job_description: str) -> str:
    """
    Generate a cache key from resume text and job description.
    
    Args:
        resume_text (str): The resume text content.
        job_description (str): The job description content.
        
    Returns:
        str: A hash-based cache key.
    """
    # Combine texts and create a hash
    combined = f"{resume_text}|{job_description}"
    return hashlib.md5(combined.encode()).hexdigest()
