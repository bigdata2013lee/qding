# --*-- coding:utf-8 --*--
import json
from django.http import HttpResponse
from django.shortcuts import redirect
from apps.common.utils.serializer import encode
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def localApi(request, apiName, method):
    url = "%s/%s" % (apiName, method)
    method = method.split('/')
    if not request.session.get('web_user', {}) and method[1]: return redirect('/')
    PACKAGE = "apps.common.api"
    path = apiName.split('/')
    apiMoudle = __import__("%s.%s" % (PACKAGE, path[0]), globals=globals(), locals=locals(), fromlist=[''])
    apiClass = getattr(apiMoudle, path[1])
    apiObj = apiClass()
    apiObj.qz_session = request.session.__dict__
    params = {}
    for k, v in request.REQUEST.items(): params[k] = v
    exeMethod = getattr(apiObj, method[0])
    result = exeMethod(**params)
    return HttpResponse(json.dumps(encode(result), ensure_ascii=False), content_type='text/html')
