# --*-- coding:utf8 --*--
from apps.common.api.brake_api import Brake_Version_Api
from test.test_data import brake_version
version_id = None


def test_brake_version_api():
    test_add_brake_version()
    test_get_brake_version_list()
    test_get_version()
    test_remove_version()


def test_add_brake_version():
    params = {
        "former_version": "",
        "version": brake_version['version'],
        "filename": "test.test",
        "md5sum": brake_version['md5sum'],
        "message": brake_version['message'],
    }
    result = Brake_Version_Api().add_brake_version(**params)
    global version_id
    version_id = result['data'].get("version_id")


def test_get_brake_version_list():
    params = {}
    Brake_Version_Api().get_brake_version_list(**params)


def test_get_version():
    params = {}
    Brake_Version_Api().get_version(**params)


def test_remove_version():
    params = {
        "version_id": version_id
    }
    Brake_Version_Api().remove_version(**params)
