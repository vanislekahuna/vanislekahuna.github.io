import json
import hashlib
from datetime import datetime, timedelta

class GeocodeCache:
    """In-memory cache for geocoding results"""
    
    def __init__(self, ttl_days=30):
        self.cache = {}
        self.ttl_days = ttl_days
    
    def _get_key(self, address):
        """Generate cache key from address"""
        return hashlib.md5(address.lower().strip().encode()).hexdigest()
    
    def get(self, address):
        """Get cached result if exists and not expired"""
        key = self._get_key(address)
        
        if key in self.cache:
            cached = self.cache[key]
            cached_time = datetime.fromisoformat(cached['timestamp'])
            
            # Check if expired
            if datetime.now() - cached_time < timedelta(days=self.ttl_days):
                print(f"[CACHE] HIT for: {address}")
                return cached['lat'], cached['lon']
            else:
                print(f"[CACHE] EXPIRED for: {address}")
                del self.cache[key]
        
        print(f"[CACHE] MISS for: {address}")
        return None, None
    
    def set(self, address, lat, lon):
        """Cache geocoding result"""
        key = self._get_key(address)
        self.cache[key] = {
            'lat': lat,
            'lon': lon,
            'timestamp': datetime.now().isoformat()
        }
        print(f"[CACHE] STORED: {address} -> ({lat}, {lon})")
    
    def get_stats(self):
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'entries': list(self.cache.keys())[:10]  # First 10 keys
        }


# Global cache instance
_cache = GeocodeCache(ttl_days=30)


def get_cache():
    """Get the global cache instance"""
    return _cache