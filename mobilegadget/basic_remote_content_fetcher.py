from remote_content_fetcher import *
import socket
import urllib, urllib2

class stopRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        raise urllib2.HTTPError(headers.get('Location'), code, msg, headers, fp)

    def http_error_302(self, req, fp, code, msg, headers):
        raise urllib2.HTTPError(headers.get('Location'), code, msg, headers, fp)

class BasicRemoteContentFetcher(RemoteContentFetcher):
    """
    Basic remote content fetcher
    """
    requests = []
	
    def fetchRequest(self, request):
        # make url
        url = request.getUrl()

        # prepare data
        data = {}
        if request.isPost():
            data = urllib.urlencode(request.getPostBody())
            handle = urllib2.Request(url, data)
        else:
            handle = urllib2.Request(url)

        # prepare headers
        headers = request.getHeaders()
        for key,val in headers.iteritems():
            if key not in ['Transfer-Encoding','Cache-Control','Expires','Content-Length']:
                handle.add_header(key, val)

        opener = urllib2.build_opener(stopRedirectHandler())

        # Execute the request
        c = opener.open(handle)
        body = c.read()
        header = '';
        header = c.info().keys()
        httpCode = c.code
        contentType = c.info().getheaders("content-type")
        if (not httpCode):
            httpCode = '404'

        request.setHttpCode(httpCode)
        request.setContentType(contentType)
        request.setResponseHeaders(header)
        request.setResponseContent(body)
        request.setResponseSize(len(body))
        c.close()
        del handle
        return request
