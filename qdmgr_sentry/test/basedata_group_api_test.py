# --*-- coding:utf8 --*--

from apps.common.api.basedata_api import Basedata_Group_Api
from test.test_data import apartment


def test_basedata_group_api():
    test_get_group_list()
    test_get_group_list_by_filter()


def test_get_group_list():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
    }
    Basedata_Group_Api().get_group_list(**params)


def test_get_group_list_by_filter():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
        "group": apartment['group'],
        "project_id": apartment['project_id'],
    }
    Basedata_Group_Api().get_group_list_by_filter(**params)
