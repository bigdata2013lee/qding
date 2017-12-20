# -*- coding:utf-8 -*-
import json
import codecs
from django.http.response import HttpResponse
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render_to_response

import logging
import csv
from apps.common.utils.sentry_date import get_str_day_by_timestamp
from apps.common.utils.serializer import encode
logger = logging.getLogger('qding')


@csrf_exempt
def index(request):
    request.session['web_user'] = {}
    return render_to_response('community/login.html', context_instance=RequestContext(request))


@csrf_exempt
def content(request):
    web_user = request.session.get('web_user', {})
    if not web_user:
        return redirect('/')
    return render_to_response('community/content.html', context_instance=RequestContext(request))


@csrf_exempt
def web_login(request):
    params = {
        'username': request.POST.get('username', ''),
        'password': request.POST.get('password', ''),
    }
    from apps.common.api.user_api import Web_User_Api
    result = Web_User_Api().web_login(**params)
    if result['data']['flag'] == 'Y':
        request.session['web_user'] = result['data']['web_user']
    return HttpResponse(json.dumps(encode(result), ensure_ascii=False), content_type='text/html')


@csrf_exempt
def web_logout(request):
    request.session['web_user'] = {}
    return redirect('/')


@csrf_exempt
def brake_config_login(request):
    params = {
        'province': request.POST.get('province', ''),
        'city': request.POST.get('city', ''),
        'community': request.POST.get('community', ''),
        'phone': request.POST.get('phone', ''),
        'brake_config_password': request.POST.get('brake_config_password', '')
    }
    from apps.common.api.user_api import Web_User_Api
    result = Web_User_Api().brake_config_login(**params)
    if result['data']['flag'] == 'Y':
        request.session['web_user'] = result['data']['web_user']
    return HttpResponse(json.dumps(encode(result), ensure_ascii=False), content_type='text/html')


@csrf_exempt
def brake_config_login_v2(request):
    params = {
        'phone': request.POST.get('phone', ''),
        'password': request.POST.get('password', '')
    }
    from apps.common.api.brake_api import Brake_Configer_Api
    result = Brake_Configer_Api().log_in(**params)
    if result['data']['flag'] == 'Y':
        request.session['web_user'] = result['data']['web_user']
        request.session['phone'] = request.POST.get('phone', '')
    return HttpResponse(json.dumps(encode(result), ensure_ascii=False), content_type='text/html')


@csrf_exempt
def download_app(request):
    return render_to_response('community/download_app.html', context_instance=RequestContext(request))


@csrf_exempt
def download_tx_app(request):
    return render_to_response('community/download_tx_app.html', context_instance=RequestContext(request))


@csrf_exempt
def go_to_ad(request):
    return render_to_response('community/go_to_ad.html', context_instance=RequestContext(request))


@csrf_exempt
def forget_password(request):
    return render_to_response('community/forget_password.html', context_instance=RequestContext(request))


@csrf_exempt
def dump_pass_list_to_excel(request):
    str_project_id_list = request.GET.get('project_id_list', '')
    start_time = request.GET.get('start_time', 0) or 0
    end_time = request.GET.get('end_time', 0) or 0
    project_id_list = []
    if str_project_id_list:
        project_id_list = str_project_id_list.split(',')

    params = {
        'outer_project_id_list': project_id_list,
        'start_time': start_time,
        'end_time': end_time,
    }
    from apps.common.api.brake_api import Brake_Pass_Api
    result = Brake_Pass_Api().get_brake_pass_by_project_id_list(**params)
    pass_data_list = result['data'].get("brake_pass_list", []) or []
    str_start_day = get_str_day_by_timestamp(int(params['start_time']))
    str_end_day = get_str_day_by_timestamp(int(params['end_time']))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=pass_data_list%s_%s.csv' % (str_start_day, str_end_day)
    response.write(codecs.BOM_UTF8)
    writer = csv.DictWriter(response, fieldnames=['city', 'community', 'phone',
                                                  'dump_user_type', 'created_time_str', 'position'],
                            extrasaction='ignore')
    titles = dict(city="城市", community="小区", phone="手机", created_time_str="通行时间",
                  dump_user_type="用户类型", position="位置")
    writer.writerow(titles)
    writer.writerows(pass_data_list)
    return response


@csrf_exempt
def dump_order_list_to_excel(request):
    str_project_id_list = request.GET.get('project_id_list', '')
    start_time = request.GET.get('start_time', 0) or 0
    end_time = request.GET.get('end_time', 0) or 0
    project_id_list = []
    if str_project_id_list:
        project_id_list = str_project_id_list.split(',')

    params = {
        'outer_project_id_list': project_id_list,
        'start_time': start_time,
        'end_time': end_time,
    }
    from apps.common.api.sentry_api import Sentry_Visitor_Api
    result = Sentry_Visitor_Api().get_visitor_list_by_project_id_list(**params)
    app_data_list = result['data'].get('brake_order_list', []) or []
    str_start_day = get_str_day_by_timestamp(int(params['start_time']))
    str_end_day = get_str_day_by_timestamp(int(params['end_time']))
    response = HttpResponse(content_type='text/csv')
    response.write(codecs.BOM_UTF8)
    response['Content-Disposition'] = 'attachment;filename=app_order_list%s_%s.csv' % (str_start_day, str_end_day)
    writer = csv.DictWriter(response, fieldnames=['city', 'community', 'room', 'phone', 'start_time', 'end_time',
                                                  'reason', 'dump_status', 'dump_valid_num'], extrasaction='ignore')
    titles = dict(city="城市", community="小区", room="房间", phone="手机", start_time="开始时间",
                  end_time="结束时间", reason="原因", dump_status="是否来访", dump_valid_num="有效次数")
    writer.writerow(titles)
    writer.writerows(app_data_list)
    return response


@csrf_exempt
def dump_brake_machine_to_excel(request):
    str_project_id_list = request.GET.get('project_id_list', '')
    project_id_list = []
    if str_project_id_list:
        project_id_list = str_project_id_list.split(',')

    params = {
        'outer_project_id_list': project_id_list,
    }

    from apps.common.api.brake_api import Brake_Machine_Api
    result = Brake_Machine_Api().get_brake_machine_by_project_id_list(**params)
    brake_machine_list = result['data'].get('brake_machine_list', []) or []
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=brake_machine_list.csv'
    response.write(codecs.BOM_UTF8)
    writer = csv.DictWriter(response,
                            fieldnames=['province', 'city', 'project', 'position_str',
                                        'updated_time_str', 'online_status_str', 'level',
                                        'mac', 'version', 'hardware_version'],
                            extrasaction='ignore')
    titles = dict(
                province='省份',
                city='城市',
                project='小区',
                position_str='位置',
                updated_time_str="最近通行时间",
                online_status_str="状态",
                level="级别",
                mac='mac',
                version='固件版本号',
                hardware_version='硬件版本号',
                )
    writer.writerow(titles)
    writer.writerows(brake_machine_list)
    return response
