from django.conf.urls import patterns, url

regex01 = r'^remote/(?P<apiName>([a-zA-z]\w+\.)+(([a-zA-Z]\w+)?Api))\.(?P<method>[a-zA-Z]\w+)/$'


urlpatterns = patterns('',
    url(r'^$', 'web.views.common_view.index'),
    url(r'^manage/$', 'web.views.common_view.manage'),
    url(r'^test.html$', 'web.views.common_view.test'),
    url(r'^wuye_logout/$', 'web.views.common_view.wuye_logout'),
    url(r'^mgr_logout/$', 'web.views.common_view.mgr_logout'),
    url(r'^test_api.html/$', 'web.views.common_view.test_api'),
    url(r'^speek/$', 'web.views.downloads_view.speek'),
    url(regex01, 'web.views.common_view.remoteView'),  # remoteView
)
