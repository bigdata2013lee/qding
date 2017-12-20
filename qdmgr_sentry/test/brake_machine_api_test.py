# --*-- coding:utf8 --*--
from apps.common.api.brake_api import Brake_Machine_Api
from test.test_data import apartment
from test.test_data import brake_machine
brake_id = None


def test_brake_machine_api():
    test_add_brake()
    test_submit_brake()
    test_get_brake_machine_by_filter()
    test_get_brake_machine_by_project_id_list()
    test_get_brake_info()
    test_get_can_pass_brake_list()
    test_get_brake_status()
    test_set_brake_heart_time()
    test_set_brake_monit()
    test_get_all_brake_machine_count()
    test_delete_brake()
    test_add_brake()


def test_add_brake():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
        "group": apartment['group'],
        "build": apartment['build'],
        "unit": apartment['unit'],
        "mac": brake_machine['mac'],
        "gate_name": brake_machine['gate_info']['gate_name'],
        "direction": brake_machine['gate_info']['direction'],
        "bluetooth_rssi": brake_machine['bluetooth_rssi'],
        "wifi_rssi": brake_machine['wifi_rssi'],
        "open_time": brake_machine['open_time'],
    }
    result = Brake_Machine_Api().add_brake(**params)
    global brake_id
    brake_id = result['data'].get('brake_id')


def test_submit_brake():
    params = {
                "brake_id": brake_id,
                "open_time": "20",
                "bluetooth_rssi": "-81",
                "wifi_rssi": "-91",
                "level": 2
              }
    Brake_Machine_Api().submit_brake(**params)


def test_get_brake_machine_by_filter():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
        "group": apartment['group'],
        "build": apartment['build'],
        "unit": apartment['unit'],
        "mac": "123123123123",
        "brake_type": "2"
    }
    Brake_Machine_Api().get_brake_machine_by_filter(**params)


def test_get_brake_machine_by_project_id_list():
    params = {
        "outer_project_id_list": [apartment['outer_project_id']]
    }
    Brake_Machine_Api().get_brake_machine_by_project_id_list(**params)


def test_get_brake_info():
    params = {
        "brake_id": brake_id
    }
    Brake_Machine_Api().get_brake_info(**params)


def test_get_can_pass_brake_list():
    params = {
        "room_id": apartment['outer_room_id']
    }
    Brake_Machine_Api().get_can_pass_brake_list(**params)


def test_get_brake_status():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
        "group": apartment['group'],
        "build": apartment['build'],
        "unit": apartment['unit'],
        "brake_type": "2"
    }
    Brake_Machine_Api().get_brake_status(**params)


def test_set_brake_heart_time():
    params = {
        "brake_id": brake_id,
        "heart_time": 123,
    }
    Brake_Machine_Api().set_brake_heart_time(**params)


def test_set_brake_monit():
    params = {
        "brake_id": brake_id,
        "is_monit": '1',
    }
    Brake_Machine_Api().set_brake_monit(**params)


def test_get_all_brake_machine_count():
    params = {}
    Brake_Machine_Api().get_all_brake_machine_count(**params)


def test_delete_brake():
    params = {"brake_id": brake_id}
    Brake_Machine_Api().delete_brake(**params)
