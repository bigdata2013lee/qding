# -*- coding: utf-8 -*-
import json
import os
from django.http.response import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from apps.common.utils.xutil import write_file
from apps.common.utils.md5 import get_md5sum
from settings.const import CONST
from apps.common.utils.serializer import encode

@csrf_exempt
def index(request):
    if not request.session.get('web_user', {}):
        return redirect('/')
    return render_to_response('manage/content.html', context_instance=RequestContext(request))


@csrf_exempt
def content(request):
    web_user = request.session.get('web_user', {})
    if not web_user: return redirect('/')

    return render_to_response('manage/content.html', context_instance=RequestContext(request))


@csrf_exempt
def add_brake_version(request):
    if not request.session.get('web_user', {}): return redirect('/')
    params = {
        "former_version": request.POST.get("former_version", ""),
        "version": request.POST.get("version", ""),
        "filename": request.FILES.get("upload_file", {})._name,
        "project_list": request.POST.get("project_list", []),
        "lowest_version": request.POST.get("lowest_version", ""),
        "message": request.POST.get("message", "")
    }
    if not os.path.exists(CONST['static']['brake_upgrade_dir']):
        os.makedirs(CONST['static']['brake_upgrade_dir'])
    file_abs_path = CONST['static']['brake_upgrade_dir'] + params['filename']
    if os.path.exists(file_abs_path):
        os.remove(file_abs_path)
    write_file(file_abs_path, request.FILES.get("upload_file", {}))
    md5sum = get_md5sum(file_abs_path)
    params['md5sum'] = md5sum
    from apps.common.api.brake_api import Brake_Version_Api
    result = Brake_Version_Api().add_brake_version(**params)
    return HttpResponse(json.dumps(encode(result), ensure_ascii=False), content_type='text/html')


@csrf_exempt
def add_brake_config_version(request):
    if not request.session.get('web_user', {}): return redirect('/')
    params = {
        "former_version": request.POST.get("former_version", ""),
        "version": request.POST.get("version", ""),
        "filename": request.FILES.get("upload_file", {})._name,
        "message": request.POST.get("message", "")
    }
    if not os.path.exists(CONST['static']['brake_upgrade_config_dir']):
        os.makedirs(CONST['static']['brake_upgrade_config_dir'])
    file_abs_path = CONST['static']['brake_upgrade_config_dir'] + params['filename']
    if os.path.exists(file_abs_path):
        os.remove(file_abs_path)
    write_file(file_abs_path, request.FILES.get("upload_file", {}))
    md5sum = get_md5sum(file_abs_path)
    params['md5sum'] = md5sum
    from apps.common.api.brake_api import Brake_Config_Version_Api
    result = Brake_Config_Version_Api().add_version(**params)
    return HttpResponse(json.dumps(encode(result), ensure_ascii=False), content_type='text/html')


@csrf_exempt
def remove_version(request):
    if not request.session.get('web_user', {}): return redirect('/')
    params = {
        "version_id": request.POST.get('version_id'),
    }
    filename = request.POST.get("file_uri", "").split("/")[-1]
    file_abs_path = CONST['static']['brake_upgrade_dir'] + filename
    from apps.common.api.brake_api import Brake_Version_Api
    result = Brake_Version_Api().remove_version(**params)
    if result['data']['flag'] == 'Y':
        if os.path.exists(file_abs_path):
            os.remove(file_abs_path)
    return HttpResponse(json.dumps(encode(result), ensure_ascii=False), content_type='text/html')


@csrf_exempt
def remove_brake_version(request):
    if not request.session.get('web_user', {}):
        return redirect('/')
    params = {
        "version_id": request.POST.get('version_id'),
    }
    filename = request.POST.get("file_uri", "").split("/")[-1]
    file_abs_path = CONST['static']['brake_upgrade_config_dir'] + filename
    from apps.common.api.brake_api import Brake_Config_Version_Api
    result = Brake_Config_Version_Api().remove_version(**params)
    if result['data']['flag'] == 'Y':
        if os.path.exists(file_abs_path):
            os.remove(file_abs_path)
    return HttpResponse(json.dumps(encode(result), ensure_ascii=False), content_type='text/html')
