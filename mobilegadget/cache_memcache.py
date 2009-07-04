from django.conf import settings
from django.core.cache import cache

class CacheMemcache():
    # using memcache_add behavior for cache stampeding prevention
    def add(self, key, value, timeout):
        try:
            cache.add(key, value, timeout)
        except:
            raise RuntimeError, "Couldn't add to cache"
	
    def get(self, key):
        try:
            return cache.get(key)
        except:
            return False
	
    def set(self, key, value):
        try:
            cache.set(key, value)
        except:
            raise RuntimeError, "Couldn't store data in cache"
	
    def delete(self, key):
        cache.delete(key)
