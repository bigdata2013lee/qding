# -*- coding:utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext


def api(request):
    return render_to_response('api.html', context_instance=RequestContext(request))
