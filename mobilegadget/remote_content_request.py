import hashlib
import re
import urllib

class RemoteContentRequest():
    # these are used for making the request
    url = ''
    headers = {}
    postBody = None
    # these fields are filled in once the request has completed
    responseContent = None
    responseSize = None
    responseHeaders = None
    httpCode = None
    contentType = None
    handle = None
    
    OPENSOCIAL_OWNERID = "opensocial_owner_id"
    OPENSOCIAL_VIEWERID = "opensocial_viewer_id"
    OPENSOCIAL_APPID = "opensocial_app_id"
    
    def __init__(self, url, headers = {}, postBody = None, req = None):
        # adding opensocial parameters
        os_param = {}

        if req.user.is_authenticated():
            self.viewer = req.user.id
            os_param[self.OPENSOCIAL_VIEWERID] = self.viewer
        if req.GET.has_key('uid'):
            self.owner = req.GET['uid']
            os_param[self.OPENSOCIAL_OWNERID] = self.owner
        m = re.match(r'^/appli/([0-9]+)/', req.path)
        if m:
            os_param[self.OPENSOCIAL_APPID] = m.group(1) 

        # conversion GET character code
        urls = url.split('?', 1)
        if len(urls) > 1 :
            raw = urllib.unquote(urls[1])
            urls[1] = urllib.quote(raw.encode('utf-8'), '=&')
            url =  '?'.join(urls)
        self.url = url

        if os_param:
            param = urllib.urlencode(os_param)
            delimiter = '&' if self.url.find('?') > 0 else '?'
            self.url += delimiter + param	

        # conversion POST charcter code
        if postBody:
            self.postBody = {}
            for k,v in postBody.items():
                self.postBody[k] = v.encode('utf-8')

        # add User-Agent Header
        self.headers = headers
        if req.META.has_key('HTTP_USER_AGENT'):
            self.headers['User-Agent'] = req.META['HTTP_USER_AGENT']

    # returns a hash code which identifies this request, used for caching
    # takes url and postbody into account for constructing the sha1 checksum
    def toHash(self):
        hashkey = self.url + (''.join(self.postBody.keys()) if self.postBody else '')
        return hashlib.sha1(hashkey).hexdigest()
	
    def getContentType(self):
        return self.contentType
	
    def getHttpCode(self):
        return self.httpCode
	
    def getResponseContent(self):
        return self.responseContent
	
    def getResponseHeaders(self):
        return self.responseHeaders
	
    def getResponseSize(self):
        return self.responseSize
	
    def getHeaders(self):
        return self.headers
	
    def isPost(self):
        return self.postBody != None
	
    def hasHeaders(self):
        return self.headers != None
	
    def getPostBody(self):
        return self.postBody
	
    def getUrl(self):
        return self.url
	
    def setContentType(self, type):
        self.contentType = type
	
    def setHttpCode(self, code):
        self.httpCode = int(code)
	
    def setResponseContent(self, content):
        self.responseContent = content
	
    def setResponseHeaders(self, headers):
        self.responseHeaders = headers
	
    def setResponseSize(self, size):
        self.responseSize = int(size)
	
    def setHeaders(self, headers):
        self.headers = headers
	
    def setPostBody(self, postBody):
        self.postBody = postBody
	
    def setUrl(self, url):
        self.url = url
