from django.conf.urls import patterns, include, url

regex01 = r'^remote/(?P<apiName>([a-zA-z]\w+\.)+(([a-zA-Z]\w+)?Api))\.(?P<method>[a-zA-Z]\w+)/$'
regex02 = r'^download/upgrade/\w+/(?P<ver_id>(\w{24}))/.+$'
regex03 = r'^download/advmedia/(?P<media_file_id>(\w{24}))$'

urlpatterns = patterns('',
    url(r'^$', 'web.views.common_view.index'),
    url(r'^manage/$', 'web.views.common_view.manage'),
    url(r'^wuye_logout/$', 'web.views.common_view.wuye_logout'),
    url(r'^mgr_logout/$', 'web.views.common_view.mgr_logout'),
    url(r'^test_api.html/$', 'web.views.common_view.test_api'),
    url(regex01, 'web.views.common_view.remoteView'),  # remoteView

    url(regex02, 'web.views.downloads_view.get_upgrade_file'),
    url(regex03, 'web.views.downloads_view.get_adv_meida_file'),

    url(r'^image/app/avatars/(?P<user_id>(\w+))$', 'web.views.downloads_view.get_image_app_avatar'),
    url(r'^image/call/index_snapshot/(?P<call_id>(\w+))$', 'web.views.downloads_view.get_call_index_snapshot'),

    url(r'^qrcode/bind_aptm/(?P<qrcode_str>(\w+))(/(?P<user_id>(\w+)))?', 'web.views.common_view.app_bind_aptm_by_qrc')


)


