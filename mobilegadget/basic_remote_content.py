from types import *
from cache_memcache import *
from remote_content import *
from remote_content_request import *
from basic_remote_content_fetcher import *

class BasicRemoteContent(RemoteContent):
    def fetch(self, request, context):
        cache = CacheMemcache()
        remoteContentFetcher = BasicRemoteContentFetcher()

        if not isinstance(request, RemoteContentRequest):
            raise("Invalid request type in remoteContent")

        # determine which requests we can load from cache, and which we have to actually fetch
        if not context.getIgnoreCache():
            cachedRequest = cache.get(request.toHash())
            if cachedRequest:
                return cachedRequest

        ret = remoteContentFetcher.fetchRequest(request)
        # only cache requests that returned a 200 OK
        if request.getHttpCode() == 200:
            cache.set(request.toHash(), ret)
        return ret
