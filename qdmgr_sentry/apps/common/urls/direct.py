# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('')
urlpatterns += patterns('',
                        url(r'^api/', 'apps.common.views.api'),
                        url(r'^manage/', include('apps.manage.urls.ajax')),
                        )

from apps.common.urls import static
urlpatterns += static.urlpatterns

from apps.common.urls import ajax as commonAjax
urlpatterns += commonAjax.urlpatterns

from apps.community.urls import ajax as communityAjax
urlpatterns += communityAjax.urlpatterns
