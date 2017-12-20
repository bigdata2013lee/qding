# --*-- coding:utf8 --*--

from apps.common.api.brake_api import Brake_Configer_Api
from test.test_data import config_user, apartment, brake_machine


def test_brake_configer_api():
    test_get_password()
    test_log_in()
    test_sync_project_data()
    test_add_brake()


def test_get_password():
    params = {
        "phone": config_user['phone'],
    }
    Brake_Configer_Api().get_password(**params)


def test_log_in():
    params = {
        "phone": config_user['phone'],
        "password": config_user['brake_config_password'],
    }
    Brake_Configer_Api().log_in(**params)


def test_sync_project_data():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
    }
    Brake_Configer_Api().sync_project_data(**params)


def test_add_brake():
    params = {
        "position": brake_machine['position'],
        "gate_info": brake_machine['gate_info'],
        "mac": brake_machine['mac'],
        "bluetooth_rssi": brake_machine['bluetooth_rssi'],
        "wifi_rssi": brake_machine['wifi_rssi'],
        "open_time": brake_machine['open_time'],
        "version": "V1.1",
    }
    Brake_Configer_Api().add_brake(**params)
