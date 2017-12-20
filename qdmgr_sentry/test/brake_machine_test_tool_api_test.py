# --*-- coding:utf8 --*--
from apps.common.api.brake_api import Brake_Machine_Test_Tool_Api
from test.test_data import config_user


def test_brake_machine_test_tool_api():
    test_check_tool_can_use()
    test_log_in()


def test_check_tool_can_use():
    params = {}
    Brake_Machine_Test_Tool_Api().check_tool_can_use(**params)


def test_log_in():
    params = {
        "phone": config_user['phone'],
        "password": config_user['brake_config_password'],
    }
    Brake_Machine_Test_Tool_Api().log_in(**params)
