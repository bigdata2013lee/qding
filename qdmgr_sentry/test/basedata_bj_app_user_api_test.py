# --*-- coding:utf8 --*--

from apps.common.api.basedata_api import Basedata_Bj_App_User_Api
from test.test_data import app_user, apartment, brake_machine


def test_basedata_bj_app_user_api():
    test_get_app_user_bind_room_list()
    test_get_app_user_bind_door_list()
    test_get_app_user_can_open_door()
    test_get_app_user_can_open_door_list()
    test_set_app_user_can_open_door_list()
    test_delete_app_user_can_open_door_list()
    test_get_app_user_id()
    test_set_app_user_room_list()
    test_get_app_user_by_filter()


def test_get_app_user_bind_room_list():
    params = {
        "phone": app_user['phone']
    }
    Basedata_Bj_App_User_Api().get_app_user_bind_room_list(**params)


def test_get_app_user_bind_door_list():
    params = {
        "phone": app_user['phone']
    }
    Basedata_Bj_App_User_Api().get_app_user_bind_room_list(**params)


def test_get_app_user_can_open_door():
    params = {
        "phone": app_user['phone']
    }
    Basedata_Bj_App_User_Api().get_app_user_can_open_door(**params)


def test_get_app_user_can_open_door_list():
    params = {
        "outer_app_user_id": app_user['outer_app_user_id'],
    }
    Basedata_Bj_App_User_Api().get_app_user_can_open_door_list(**params)


def test_set_app_user_can_open_door_list():
    params = {
        "phone": app_user['phone'],
        "brake_mac_list": [brake_machine['mac']]
    }
    Basedata_Bj_App_User_Api().set_app_user_can_open_door_list(**params)


def test_delete_app_user_can_open_door_list():
    params = {
        "phone": app_user['phone'],
        "brake_mac_list": [brake_machine['mac']]
    }
    Basedata_Bj_App_User_Api().delete_app_user_can_open_door_list(**params)


def test_get_app_user_id():
    params = {
        "outer_app_user_id": app_user['outer_app_user_id'],
    }
    Basedata_Bj_App_User_Api().get_app_user_id(**params)


def test_set_app_user_room_list():
    params = {
        "phone": app_user['phone'],
    }
    Basedata_Bj_App_User_Api().set_app_user_room_list(**params)


def test_get_app_user_by_filter():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
        "outer_app_user_id": app_user['outer_app_user_id'],
        "app_user_id": app_user['app_user_id'],
        "phone": app_user['phone'],
    }
    Basedata_Bj_App_User_Api().get_app_user_by_filter(**params)
