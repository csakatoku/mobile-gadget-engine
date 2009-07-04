# -*- coding: utf-8 -*-
import urllib
from urllib2 import HTTPError

from django.shortcuts import render_to_response
from django.http import HttpResponse

from mobilegadget.http.gadget_rendering_servlet import GadgetRenderingServlet
from mobilegadget.gadget import *
from mobilegadget.gadget_context import *
from mobilegadget.gadget_server import *

OPENSOCIAL_APP_ID = 1
OPENSOCIAL_MOBILE_GADGET_URL = 'http://127.0.0.1:9088/'

def render(req, mode):
    url = req.POST.get('url') or req.GET.get('url')
    if url is None:
        url = OPENSOCIAL_MOBILE_GADGET_URL

    if not url.startswith('http'):
        m = re.match(r'^(https?://[^/]+)', OPENSOCIAL_MOBILE_GADGET_URL)
        url = m.group(1) + url

    # Rendering gadget contents for mobile phone
    cs = GadgetRenderingServlet(OPENSOCIAL_APP_ID, url, req, timeout=10)

    try:
        output = cs.doGet(mode)
    except HTTPError, e:
        if e.code in (301, 302):
            newurl = e.filename
            if newurl is not None:
                # conversion GET character code
                try:
                    urls = newurl.split('?', 1)
                    if len(urls) > 1 :
                        raw = urllib.unquote(urls[1]).decode('utf-8')
                        urls[1] = urllib.quote(raw.encode('cp932'), '=')
                        newurl =  '%3F'.join(urls)
                except:
                    newurl = newurl.replace('?', '%3F')
                    newurl = newurl.replace('&', '%26')

                return HttpResponseRedirect('%s?url=%s' % (reverse('canvas_view'), newurl))
        output = u'エラーが発生しました。<br />しばらく経ってから、お試しください。'
    except:
        output = u'エラーが発生しました。<br />しばらく経ってから、お試しください。'
        raise

    return HttpResponse(output)
