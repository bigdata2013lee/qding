# -*- coding:utf8 -*-
import time
import json
import traceback
from apps.common.classes.User_Request import User_Request
from apps.common.utils import qd_result, validate
from apps.common.utils.sentry_date import get_day_datetime
from apps.common.utils.view_tools import jsonResponse
from apps.common.utils.xutil import create_random_num
from apps.common.utils.request_api import request_bj_server
from settings.const import CONST
from apps.web.classes.Web_User import Web_User
from apps.common.utils.redis_client import Redis_Client
rc = Redis_Client()


class Common_Api(object):
    '''
    @note: 公共方法封装在此类
    '''

    @jsonResponse()
    def get_verify_code(self, phone):
        '''
        @note: 方法用途：获取验证码
        @note: 访问url:/common_api/Common_Api/get_verify_code/
        @note: 测试demo:{phone:"18188621491"}
        @param phone: 手机号
        @return: 
        '''
        try:
            result = qd_result.get_default_result()
            phone_flag, phone_str = validate.validate_phone(str(phone))
            if not phone_flag: return qd_result.set_err_msg(result, phone_str)
            phone = str(phone)
            web_user = Web_User(phone=phone).get_user_by_phone()
            if not web_user: return qd_result.set_err_msg(result, '手机号不存在')
            verify_code = create_random_num(6)
            verify_code_created_time = int(time.time())
            verify_dic = rc.get(phone)
            if verify_dic:
                verify_dic = json.loads(verify_dic.decode('utf8'))
                former_verify_code_created_time = verify_dic.get("verify_code_created_time", 0) or 0
                if verify_code_created_time - former_verify_code_created_time < 60:
                    return qd_result.set_err_msg(result, '一分钟内不可重复获取')
            verify_dic = {'verify_code': verify_code, 'verify_code_created_time': verify_code_created_time}
            rc.set(phone, json.dumps(verify_dic), 300)
            url = CONST['bj_api_url']['api_method']['sms_request'] % (phone, verify_code)
            request_bj_server(method_url=url, method_params={}, post_flag=False)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class User_Request_Api(object):
    """
    url:/common_api/User_Request_Api/get_day_request_count/
    """
    @jsonResponse()
    def get_day_request_count(self):
        try:
            result = qd_result.get_default_result()
            day = get_day_datetime()
            result['data']['request_count'] = User_Request.get_request_day_count(day)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_day_most_busy_url(self):
        try:
            result = qd_result.get_default_result()
            day = get_day_datetime()
            result['data']['url'] = User_Request.get_request_day_count(day)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result