# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r"^(?P<apiName>\w+/(\w+))/(?P<method>\w+/(\w*))", 'apps.common.utils.apiView.localApi'),
                       )
