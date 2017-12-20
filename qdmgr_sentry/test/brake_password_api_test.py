# --*-- coding:utf8 --*--
from apps.common.api.brake_api import Brake_Password_Api
from test.brake_pass_api_test import test_set_user_pass
from test.test_data import apartment, app_user


def test_brake_password_api():
    test_add_password()


def test_add_password():
    params = {
        "room_id": apartment['outer_room_id'],
        "app_user_id": app_user['outer_app_user_id'],
        "reason": "test",
    }
    return Brake_Password_Api().add_password(**params)


def test_password():
    result = test_add_password()
    password = result['data'].get("password", "")
    # test_set_user_pass("2", password)