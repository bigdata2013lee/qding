# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^$', 'apps.community.views.index'),
                       url(r'^content$', 'apps.community.views.content'),
                       url(r'^web_login$', 'apps.community.views.web_login'),
                       url(r'^web_logout$', 'apps.community.views.web_logout'),
                       url(r'^download_app$', 'apps.community.views.download_app'),
                       url(r'^d$', 'apps.community.views.download_app'),
                       url(r'^i$', 'apps.community.views.go_to_ad'),
                       url(r'^brake_config_login$', 'apps.community.views.brake_config_login'),
                       url(r'^brake_config_login_v2$', 'apps.community.views.brake_config_login_v2'),
                       url(r'^dl$', 'apps.community.views.download_app'),
                       url(r'^download_tx_app$', 'apps.community.views.download_tx_app'),
                       url(r'^dump_pass_list_to_excel$', 'apps.community.views.dump_pass_list_to_excel'),
                       url(r'^dump_order_list_to_excel$', 'apps.community.views.dump_order_list_to_excel'),
                       url(r'^dump_brake_machine_to_excel$', 'apps.community.views.dump_brake_machine_to_excel'),
                       url(r'^forget_password$', 'apps.community.views.forget_password'),
                       )
