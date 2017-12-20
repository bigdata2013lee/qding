# --*-- coding: utf8 --*--
import time, json, traceback
from apps.common.utils.redis_client import rc


def collect():
    from apps.common.api.brake_api import Brake_Pass_Api
    bpa = Brake_Pass_Api()
    while True:
        try:
            tmp = rc.cnn.spop('user_pass_set')
            if not tmp:
                time.sleep(1)
            else:
                tmp = json.loads(tmp.decode('utf8'))
                created_time = tmp.get('created_time', None)
                mac = tmp.get('mac', None)
                pass_type = tmp.get('pass_type', None)
                app_user_id = tmp.get('app_user_id', None)
                # server_id = tmp.get('server_id', None)
                # bpa.set_user_pass(created_time, mac, pass_type, app_user_id, server_id)
                pass_mode = tmp.get('pass_mode', 100)
                pass_code = tmp.get('pass_result_code', 0)
                bpa.set_user_try_pass(created_time, mac, pass_type, app_user_id, pass_mode, pass_code)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
