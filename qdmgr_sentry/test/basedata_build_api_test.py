# --*-- coding:utf8 --*--
from apps.common.api.basedata_api import Basedata_Build_Api
from test.test_data import apartment


def test_basedata_build_api():
    test_get_build_list()
    test_get_build_list_by_filter()


def test_get_build_list():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
        "group": apartment['group'],
    }
    Basedata_Build_Api().get_build_list(**params)


def test_get_build_list_by_filter():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
        "group": apartment['group'],
        "build": apartment['build'],
        "project_id": apartment['project_id'],
        "group_id": apartment['group_id'],
    }
    Basedata_Build_Api().get_build_list_by_filter(**params)
