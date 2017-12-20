#coding=utf8
import re
import json
import logging

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from conf.api_conf import api_map
from models.account import MgrUser

log = logging.getLogger('django')



def test(request):
    context = {}
    rep = render(request, "test.html", context=context)
    return rep


def index(request):
    context={}
    host_name = request.get_host()
    log.debug("index from host:%s", host_name)
    login_page = "wy_login.html"

    if not re.findall("^\w*wy\w+\.", host_name): login_page = "mgr_login.html"

    return render(request, login_page, context=context)






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


    return HttpResponseRedirect('/')


def test_api(request):
    context = {}
    return render(request, "test_api.html", context=context)


def remoteView(request, apiName, method):
    """
    Json Rpc view
    :param request:
    :param apiName:
    :param method:
    :return:
    """
    from apis.base import api_thread_local
    api_thread_local.request = request
    api_inst = api_map.get(apiName, None)

    if not re.findall("^[a-zA-Z]\w+$", method):
        raise Http404("Api method name is illegal.")
    elif not api_inst:
        raise Http404("Api Name name is illegal.")

    log.debug('###===Api:%s.%s' % (apiName, method))
    params = "{}"

    if request.method == "POST":
        params = request.POST.get("_params", '{}')
    elif request.method == "GET":
        params = request.GET.get("_params", '{}')

    params = json.loads(params)
    # log.debug('###===Params: %s', params)

    exec_method = getattr(api_inst, method, None)
    if not exec_method or getattr(exec_method, "_rpc_disable", False):
        raise Http404("Api method name is illegal.")

    result = exec_method(**params)

    if isinstance(result, dict) and isinstance(result.get('data', {}), dict) \
            and not result.get('data', {}).get('collection', []):

        log.debug("result:%s", result)

    if isinstance(result, HttpResponse):
        return result

    return HttpResponse(json.dumps(result, ensure_ascii=False))


def mgr_logout(request):
    request.session['mgr_user_id'] = ""
    request.session.flush()
    return HttpResponseRedirect("/")




