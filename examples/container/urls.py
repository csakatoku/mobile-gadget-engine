# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'container.views',
    url('^canvas/$', 'render',
        dict(mode='canvas'),
        name='canvas_view'),

    url('^profile/$', 'render',
        dict(mode='profile'),
        name='profile_view'),
)
