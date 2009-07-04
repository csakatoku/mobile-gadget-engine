"""
 * remoteContent* classes, we departed from the shindig java base style a bit here
 * We want to use curl_multi for our content fetching because we don't have any fancy 
 * worker queue's where the java variant does. 
 * So a different methodlogy which calls for a different working unfortunatly, however
 * it's kept in the spirit of the java variant as much as possible
"""

class RemoteContent():
    def fetch(self, request, context):
        pass
