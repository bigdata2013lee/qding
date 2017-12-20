# -*- coding: utf-8 -*-

from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'sentry', 'apps.common.urls.direct', name='sentry'),
)


