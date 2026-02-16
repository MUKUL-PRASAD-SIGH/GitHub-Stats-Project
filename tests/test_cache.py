"""Tests for cache functionality."""
import pytest
import time
from app.cache import Cache


class TestCache:
    """Test cache implementation."""
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get."""
        cache = Cache()
        cache.set("test_key", "test_value")
        
        assert cache.get("test_key") == "test_value"
    
    def test_cache_get_nonexistent(self):
        """Test getting non-existent key."""
        cache = Cache()
        
        assert cache.get("nonexistent") is None
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = Cache()
        cache.set("test_key", "test_value", ttl=1)  # 1 second TTL
        
        # Should exist immediately
        assert cache.get("test_key") == "test_value"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get("test_key") is None
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_cache_overwrite(self):
        """Test overwriting cached value."""
        cache = Cache()
        cache.set("test_key", "value1")
        cache.set("test_key", "value2")
        
        assert cache.get("test_key") == "value2"
    
    def test_cache_different_types(self):
        """Test caching different data types."""
        cache = Cache()
        
        cache.set("string", "test")
        cache.set("int", 123)
        cache.set("list", [1, 2, 3])
        cache.set("dict", {"key": "value"})
        
        assert cache.get("string") == "test"
        assert cache.get("int") == 123
        assert cache.get("list") == [1, 2, 3]
        assert cache.get("dict") == {"key": "value"}
