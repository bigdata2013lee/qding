#coding=utf8
import re
import json
import logging

import datetime
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render


from conf.api_conf import api_map
from models.account import WuyeUser, MgrUser

log = logging.getLogger('django')



def test(request):

    log.debug(request.REQUEST)
    return HttpResponse("")

def index(request):
    context={}
    host_name = request.get_host()
    log.debug("index from host:%s", host_name)
    login_page = "wy_login.html"

    if not re.findall("^\w*wy\w+\.", host_name): login_page = "mgr_login.html"

    return render(request, login_page, context=context)


def wy_manage(request):

    context = {}
    user_id = request.session.get("wuye_user_id", "")
    if not user_id:
        return HttpResponseRedirect('/')
    
    user = WuyeUser.objects(id=user_id).first()
    if not user:
        return HttpResponseRedirect('/')

    project = user.project
    context['select_project_id'] = str(project.id)
    context['select_project_name'] = project.name

    rep = render(request, "wy_manage.html", context=context)
    return rep

def mgr_manage(request):

    context = {}
    user_id = request.session.get("mgr_user_id", "")
    if not user_id:
        return HttpResponseRedirect('/')

    user = MgrUser.objects(id=user_id).first()
    if not user:
        return HttpResponseRedirect('/')

    rep = render(request, "mgr_manage.html", context=context)
    return rep


def manage(request):
    wy_user_id = request.session.get("wuye_user_id", "")
    mgr_user_id = request.session.get("mgr_user_id", "")

    log.debug("wy:%s, mgr:%s", wy_user_id, mgr_user_id)
    if wy_user_id:
        return wy_manage(request)

    elif mgr_user_id:
        return mgr_manage(request)

    return HttpResponseRedirect('/')


def test_api(request):
    context = {}
    return render(request, "test_api.html", context=context)


def remoteView(request, apiName, method):
    """

    :param request:
    :param apiName:
    :param method:
    :return:
    """

    Api_Class = api_map.get(apiName, None)

    if re.findall('^_', method):
        raise Exception("Api method name is illegal.")
    elif not Api_Class:
        raise Exception("Api Name name is illegal.")

    log.debug('\n\n###===Api:%s.%s' % (Api_Class, method))
    params = {}
    apiObj = Api_Class()
    apiObj.request = request

    params = "{}"
    if request.method == "GET":
        params = request.GET.get("_params", '{}')
    elif request.method == "POST":
        params = request.POST.get("_params", '{}')

    params = json.loads(params)
    log.debug('###===Params: %s', params)

    exec_method = getattr(apiObj, method)
    result = exec_method(**params)

    if isinstance(result, dict) and isinstance(result.get('data', {}), dict) \
            and not result.get('data', {}).get('collection', []):

        log.debug("result:%s", result)

    if isinstance(result, HttpResponse):
        return result

    return HttpResponse(json.dumps(result, ensure_ascii=False))


def wuye_logout(request):
    request.session['wuye_user_id'] = ""
    request.session.flush()
    return HttpResponseRedirect("/")


def mgr_logout(request):
    request.session['mgr_user_id'] = ""
    request.session.flush()
    return HttpResponseRedirect("/")


def app_bind_aptm_by_qrc(request, qrcode_str, user_id):
    """
    打开二维码中的URL进入到这个View中，完成二维码扫描绑定房间的功能

    1.原URL是这样的 http(s)://$host/qrcode/bind_aptm/$qrcode_str
    2.App正确扫描后补充用户信息，形成这样的URL: http(s)://$host/qrcode/bind_aptm/$qrcode_str/$user_id
    3.未经小亲象App正确扫描打开的Url会跳转到特定的Web界面(引导用户下载App)
    4.App正确扫描后，Web返回Api执行的结果(json格式)

    :param request:
    :param qrcode_str:
    :param user_id:
    :return:
    """
    from apis.qduser import QdUserQRCodeApi
    app_user_id = request.session.get('app_user_id', "")
    if not qrcode_str or not user_id or not app_user_id:
        return HttpResponseRedirect("/static/help/app-help.html")

    qduser_qrcode_api = QdUserQRCodeApi()._set_request(request)
    result = qduser_qrcode_api.app_bind_aptm_by_qrc(qrcode_str, user_id)
    return HttpResponse(json.dumps(result, ensure_ascii=False))


