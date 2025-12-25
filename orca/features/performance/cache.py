"""
Response caching system for Orca OS.
Caches LLM responses and system context for improved performance.
"""

import logging
import hashlib
import json
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class ResponseCache:
    """Cache system for LLM responses and system context."""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl: int = 3600):
        """Initialize response cache.
        
        Args:
            cache_dir: Directory for cache storage (default: ~/.orca/cache)
            ttl: Time-to-live for cache entries in seconds (default: 1 hour)
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.orca/cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }
    
    def _get_cache_key(self, query: str, context_hash: Optional[str] = None) -> str:
        """Generate cache key from query and context."""
        key_data = f"{query}:{context_hash or ''}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key."""
        return self.cache_dir / f"{key}.json"
    
    def get(self, query: str, context_hash: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached response for query.
        
        Returns:
            Cached response dict or None if not found/expired
        """
        try:
            key = self._get_cache_key(query, context_hash)
            cache_path = self._get_cache_path(key)
            
            if not cache_path.exists():
                self.stats['misses'] += 1
                return None
            
            # Load cache entry
            with open(cache_path, 'r') as f:
                cache_entry = json.load(f)
            
            # Check if expired
            cached_time = datetime.fromisoformat(cache_entry['timestamp'])
            age = (datetime.now() - cached_time).total_seconds()
            
            if age > self.ttl:
                # Expired, remove it
                cache_path.unlink()
                self.stats['evictions'] += 1
                self.stats['misses'] += 1
                return None
            
            # Cache hit
            self.stats['hits'] += 1
            return cache_entry['response']
        
        except Exception as e:
            logger.error(f"Error getting cache entry: {e}")
            self.stats['misses'] += 1
            return None
    
    def set(
        self,
        query: str,
        response: Dict[str, Any],
        context_hash: Optional[str] = None,
        custom_ttl: Optional[int] = None
    ):
        """Cache a response.
        
        Args:
            query: The query string
            response: The response to cache
            context_hash: Optional context hash for cache key
            custom_ttl: Optional custom TTL for this entry
        """
        try:
            key = self._get_cache_key(query, context_hash)
            cache_path = self._get_cache_path(key)
            
            cache_entry = {
                'query': query,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'ttl': custom_ttl or self.ttl
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_entry, f, indent=2)
            
            self.stats['sets'] += 1
            logger.debug(f"Cached response for query: {query[:50]}")
        
        except Exception as e:
            logger.error(f"Error setting cache entry: {e}")
    
    def invalidate(self, query: Optional[str] = None, pattern: Optional[str] = None):
        """Invalidate cache entries.
        
        Args:
            query: Exact query to invalidate
            pattern: Pattern to match queries (if query not provided)
        """
        try:
            if query:
                key = self._get_cache_key(query)
                cache_path = self._get_cache_path(key)
                if cache_path.exists():
                    cache_path.unlink()
                    self.stats['evictions'] += 1
            elif pattern:
                # Remove all cache files matching pattern
                for cache_file in self.cache_dir.glob("*.json"):
                    try:
                        with open(cache_file, 'r') as f:
                            cache_entry = json.load(f)
                            if pattern.lower() in cache_entry.get('query', '').lower():
                                cache_file.unlink()
                                self.stats['evictions'] += 1
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
    
    def clear(self):
        """Clear all cache entries."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            self.stats['evictions'] += len(list(self.cache_dir.glob("*.json")))
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(list(self.cache_dir.glob("*.json")))
        hit_rate = (self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) * 100) if (self.stats['hits'] + self.stats['misses']) > 0 else 0
        
        return {
            'total_entries': total_entries,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'sets': self.stats['sets'],
            'evictions': self.stats['evictions'],
            'hit_rate': hit_rate,
            'cache_dir': str(self.cache_dir)
        }
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        try:
            removed = 0
            now = datetime.now()
            
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        cache_entry = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cache_entry['timestamp'])
                    ttl = cache_entry.get('ttl', self.ttl)
                    age = (now - cached_time).total_seconds()
                    
                    if age > ttl:
                        cache_file.unlink()
                        removed += 1
                except Exception:
                    # Invalid cache file, remove it
                    cache_file.unlink()
                    removed += 1
            
            if removed > 0:
                self.stats['evictions'] += removed
                logger.info(f"Cleaned up {removed} expired cache entries")
        
        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {e}")


class ContextCache:
    """Cache for system context to avoid repeated expensive operations."""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl: int = 300):
        """Initialize context cache.
        
        Args:
            cache_dir: Directory for cache storage
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.orca/cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self.context_file = self.cache_dir / "context.json"
    
    def get_context_hash(self, context: Dict[str, Any]) -> str:
        """Generate hash for context."""
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()
    
    def get_cached_context(self) -> Optional[Tuple[Dict[str, Any], str]]:
        """Get cached system context.
        
        Returns:
            Tuple of (context_dict, hash) or None if not found/expired
        """
        try:
            if not self.context_file.exists():
                return None
            
            with open(self.context_file, 'r') as f:
                cache_entry = json.load(f)
            
            # Check if expired
            cached_time = datetime.fromisoformat(cache_entry['timestamp'])
            age = (datetime.now() - cached_time).total_seconds()
            
            if age > self.ttl:
                # Expired
                self.context_file.unlink()
                return None
            
            return (cache_entry['context'], cache_entry['hash'])
        
        except Exception as e:
            logger.error(f"Error getting cached context: {e}")
            return None
    
    def cache_context(self, context: Dict[str, Any], context_hash: str):
        """Cache system context."""
        try:
            cache_entry = {
                'context': context,
                'hash': context_hash,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.context_file, 'w') as f:
                json.dump(cache_entry, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error caching context: {e}")

