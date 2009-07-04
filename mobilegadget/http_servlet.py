import socket

class HttpServlet():
    lastModified = False;
    contentType = 'text/html'
    charset = 'UTF-8'
    noHeaders = False
    noCache = False
    moduleId = None
	
    def __init__(self, mid, url, request, timeout=2):
        self.moduleId = int(mid)
        self.url = url
        self.request = request

        self.defaulttimeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
 	
    """
    * Enter description here...
    * If noHeaders is false, it adds all the correct http/1.1 headers to the
    * request and deals with modified/expires/e-tags/etc. This makes the
    * server behave more like a real http server.
    """
    def __del__(self):
        socket.setdefaulttimeout(self.defaulttimeout)
        
    """
    * Sets the content type of this request
    * (forinstance: text/html or text/javascript, etc) 
    *
    * @param string $type content type header to use
    """
    def setContentType(self, type):
        self.contentType = type
	
    """
    * Returns the current content type 
    *
    * @return string content type string
    """
    def getContentType(self):
        return self.contentType
	
    """
    * returns the current last modified time stamp
    *
    * @return int timestamp
    """
    def getLastModified(self):
        return self.lastModified
    
    """
    * Sets the last modified timestamp. It automaticly checks if this timestamp
    * is larger then its current timestamp, and if not ignores the call
    *
    * @param int $modified timestamp
    """
    def setLastModified(self, modified):
        self.lastModified = max(self.lastModified, modified)
	
    """
    * Sets the noCache boolean. If its set to true, no-caching headers will
    * be send (pragma no cache, expiration in the past)
    *
    * @param boolean $cache send no-cache headers?
    """
    def setNoCache(self, cache = False):
        self.noCache = cache
	
    """
    * returns the noCache boolean
    *
    * @return boolean
    """
    def getNoCache(self):
        return self.noCache

    """
    * Sets the time in seconds that the browser's cache should be 
    * considered out of date (through the Expires header) 
    *
    * @param int $time time in seconds
    """
    def setCacheTime(self, time):
        self.cacheTime = time

    """
    * Returns the time in seconds that the browser is allowed to cache the
    * content
    *
    * @return int $time
    """
    def getCacheTime(self):
        return self.cacheTime
