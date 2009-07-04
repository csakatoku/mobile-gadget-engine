# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext

def default(req):
    ctxt = RequestContext(req)
    return render_to_response('base.xml', ctxt)

