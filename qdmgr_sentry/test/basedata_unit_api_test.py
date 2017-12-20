# --*-- coding:utf8 --*--
from apps.common.api.basedata_api import Basedata_Unit_Api
from test.test_data import apartment


def test_basedata_unit_api():
    test_get_unit_list()
    test_get_unit_list_by_filter()


def test_get_unit_list():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
        "group": apartment['group'],
        "build": apartment['build'],
    }
    Basedata_Unit_Api().get_unit_list(**params)


def test_get_unit_list_by_filter():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
        "group": apartment['group'],
        "build": apartment['build'],
        "unit": apartment['unit'],
        "project_id": apartment['project_id'],
        "group_id": apartment['group_id'],
        "build_id": apartment['build_id'],
    }
    Basedata_Unit_Api().get_unit_list_by_filter(**params)
