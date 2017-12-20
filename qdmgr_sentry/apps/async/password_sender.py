# --*-- coding: utf8 --*--
import time
import json
from settings.const import CONST
from apps.common.utils.redis_client import rc
from apps.common.utils.request_api import request_bj_server

domain_root = CONST['sz_api_url']['api_url']
method_url = CONST['sz_api_url']['api_method']['send_password']


def send_password_to_cloud_talker():
    while True:
        try:
            params_dict = rc.got("send_password_to_cloud_talker")
            if not params_dict:
                time.sleep(1)
            else:
                tmp_params = {
                    "topic": "bj/memjin_pwd",
                    "data": {
                        "member_id": params_dict['member_id'],
                        "pwd": params_dict['pwd'],
                        "valid_num": params_dict['valid_num'],
                        "start_time": params_dict['start_time'],
                        "end_time": params_dict['end_time'],
                        "room_id": params_dict['room_id'],
                    }
                }
                method_params = {
                    "_params": json.dumps(tmp_params)

                }
                request_bj_server(method_url=method_url, domain_root=domain_root, method_params=method_params)
        except Exception as e:
            pass
