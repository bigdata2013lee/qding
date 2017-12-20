# --*-- coding:utf8 --*--

from apps.common.api.brake_api import Brake_Log_Api
from test.test_data import brake_machine, app_user


def test_brake_log_api():
    test_add_err_log()
    test_get_app_user_err_log()
    test_get_brake_err_log()

def test_add_err_log():
    params = {
        "err_log_list": [{
            "occur_time": "1444631626",
            "brake_mac": brake_machine['mac'],
            "brake_type": "0",
            "phone_info": "",
            "app_user_id": app_user['outer_app_user_id'],
            "reason": "test",
        }]
    }
    Brake_Log_Api().add_err_log(**params)


def test_get_app_user_err_log():
    params = {
        "phone": app_user['phone']
    }
    Brake_Log_Api().get_app_user_err_log(**params)


def test_get_brake_err_log():
    params = {
        "mac": brake_machine['mac'],
    }
    Brake_Log_Api().get_brake_err_log(**params)
