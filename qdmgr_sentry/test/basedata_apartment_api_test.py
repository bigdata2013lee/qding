# --*-- coding:utf8 --*--
from apps.common.api.basedata_api import Basedata_Apartment_Api
from test.test_data import apartment


def test_basedata_apartment_api():
    test_get_apartment_by_filter()
    test_get_room_list()


def test_get_apartment_by_filter():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
        "group": apartment['group'],
        "build": apartment['build'],
        "unit": apartment['unit'],
        "room": apartment['room'],
        "project_id": apartment['project_id'],
        "group_id": apartment['group_id'],
        "build_id": apartment['build_id'],
        "unit_id": apartment['unit_id'],
        "room_id": apartment['outer_room_id'],
    }
    Basedata_Apartment_Api().get_apartment_by_filter(**params)


def test_get_room_list():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
        "group": apartment['group'],
        "build": apartment['build'],
        "unit": apartment['unit'],
    }
    Basedata_Apartment_Api().get_room_list(**params)
