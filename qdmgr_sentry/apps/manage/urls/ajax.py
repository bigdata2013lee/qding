# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^$', 'apps.manage.views.index'),
                       url(r'^content/$', 'apps.manage.views.content'),
                       url(r'^add_brake_version/$', 'apps.manage.views.add_brake_version'),
                       url(r'^add_brake_config_version/$', 'apps.manage.views.add_brake_config_version'),
                       url(r'^remove_version/$', 'apps.manage.views.remove_version'),
                       url(r'^remove_brake_version/$', 'apps.manage.views.remove_brake_version'),
                       )

