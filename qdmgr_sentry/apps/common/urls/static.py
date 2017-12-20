# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
import os

urlpatterns = patterns('',
                       url(r'^static/admin/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': os.path.join(settings.BASE_DIR, 'static/admin'), 'show_indexes': True}),
                       url(r'^static/common/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': os.path.join(settings.BASE_DIR, 'apps/common/static/common'),
                            'show_indexes': True}),
                       url(r'^static/manage/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': os.path.join(settings.BASE_DIR, 'apps/manage/static/manage'),
                            'show_indexes': True}),
                       url(r'^static/community/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': os.path.join(settings.BASE_DIR, 'apps/community/static/community'),
                            'show_indexes': True}),
                       url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': os.path.join(settings.BASE_DIR, 'uploads/'), 'show_indexes': True})
                       )
