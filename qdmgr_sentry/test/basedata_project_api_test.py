# --*-- coding:utf8 --*--

from apps.common.api.basedata_api import Basedata_Project_Api
from test.test_data import apartment


def test_basedata_project_api():
    test_sync_project_data()
    test_get_province_list()
    test_get_city_list_by_province()
    test_get_city_list()
    test_get_project_list_by_filter()
    test_get_all_project_count()
    test_refresh_project_data()
    test_find_project_by_name_from_bj()
    test_get_project_brake_machine_count()


def test_get_province_list():
    params = {}
    Basedata_Project_Api().get_province_list(**params)


def test_get_city_list_by_province():
    params = {
        "province": apartment['province'],
    }
    Basedata_Project_Api().get_city_list_by_province(**params)


def test_get_city_list():
    params = {}
    Basedata_Project_Api().get_city_list(**params)


def test_get_project_list_by_city():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
    }
    Basedata_Project_Api().get_project_list_by_city(**params)


def test_get_project_list_by_filter():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "project": apartment['project'],
    }
    Basedata_Project_Api().get_project_list_by_filter(**params)


def test_get_all_project_count():
    params = {}
    Basedata_Project_Api().get_all_project_count(**params)


def test_refresh_project_data():
    params = {
        "project_id": apartment['outer_project_id'],
    }
    Basedata_Project_Api().refresh_project_data(**params)


def test_sync_project_data():
    params = {
        "project_id": apartment['outer_project_id'],
    }
    Basedata_Project_Api().sync_project_data(**params)


def test_find_project_by_name_from_bj():
    params = {
        "project_name": apartment['project'],
    }
    Basedata_Project_Api().find_project_by_name_from_bj(**params)


def test_get_project_brake_machine_count():
    params = {
        "outer_project_id": apartment['outer_project_id'],
    }
    Basedata_Project_Api().get_project_brake_machine_count(**params)

