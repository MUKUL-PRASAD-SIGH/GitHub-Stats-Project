"""Simple in-memory cache with TTL support."""
import time
from typing import Any, Optional
from .config import settings


class Cache:
    """In-memory cache with time-to-live (TTL) expiration."""
    
    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key not in self._store:
            return None
        
        value, expiry = self._store[key]
        
        if time.time() > expiry:
            # Expired, remove from cache
            del self._store[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (defaults to settings.cache_ttl)
        """
        if ttl is None:
            ttl = settings.cache_ttl
        
        expiry = time.time() + ttl
        self._store[key] = (value, expiry)
    
    def clear(self) -> None:
        """Clear all cached values."""
        self._store.clear()
    
    def size(self) -> int:
        """Return number of cached items."""
        return len(self._store)


# Global cache instance
cache = Cache()
