# --*-- coding:utf8 --*--
from apps.common.api.brake_api import Brake_Pass_Api
from apps.common.utils.redis_client import Redis_Client
import time
from test.test_data import app_user, brake_machine, apartment


def test_brake_pass_api():
    test_set_user_pass_list()
    test_set_user_pass()
    test_get_pass_list_by_position()
    test_get_community_day_pass_count()
    test_get_all_pass_count()
    test_get_user_pass_list()
    test_get_user_pass_list_by_phone()
    test_get_brake_pass_list()


def test_set_user_pass_list():
    params = {
        "user_pass_list": [{
            "created_time": int(time.time()),
            "mac": brake_machine['mac'],
            "pass_type": "0",
            "app_user_id": app_user['app_user_id']
        }]
    }
    Brake_Pass_Api().set_user_pass_list(**params)


def test_set_user_pass(pass_type="0", pass_id=app_user['app_user_id']):
    params = {
        "created_time": int(time.time()),
        "mac": brake_machine['mac'],
        "pass_type": pass_type,
        "app_user_id": pass_id,
        "rc": Redis_Client(),
    }
    Brake_Pass_Api().set_user_pass(**params)


def test_get_pass_list_by_position():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
    }
    Brake_Pass_Api().get_pass_list_by_position(**params)


def test_get_community_day_pass_count():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "community": apartment['project'],
    }
    Brake_Pass_Api().get_community_day_pass_count(**params)


def test_get_all_pass_count():
    params = {}
    Brake_Pass_Api().get_all_pass_count(**params)


def test_get_user_pass_list():
    params = {
        "app_user_id": app_user['outer_app_user_id']
    }
    Brake_Pass_Api().get_user_pass_list(**params)


def test_get_user_pass_list_by_phone():
    params = {
        "phone": app_user['phone']
    }
    Brake_Pass_Api().get_user_pass_list_by_phone(**params)


def test_get_brake_pass_list():
    params = {
        "mac": brake_machine['mac']
    }
    Brake_Pass_Api().get_brake_pass_list(**params)
