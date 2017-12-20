# --*-- coding:utf8 --*--
from apps.common.api.brake_api import Brake_Config_Version_Api
from test.test_data import brake_config_version
version_id = None


def test_brake_config_version_api():
    test_check_upgrade()
    test_add_version()
    test_get_version_list()
    test_remove_version()


def test_check_upgrade():
    params = {
        "version": ""
    }
    Brake_Config_Version_Api().check_upgrade(**params)


def test_add_version():
    params = {
        "former_version": brake_config_version['former_version'],
        "version": brake_config_version['version'],
        "filename": "test.tt",
        "md5sum": brake_config_version['md5sum'],
        "message": brake_config_version['message'],
    }
    global version_id
    result = Brake_Config_Version_Api().add_version(**params)
    version_id = result['data'].get("version_id")


def test_get_version_list():
    params = {}
    Brake_Config_Version_Api().get_version_list(**params)


def test_remove_version():
    params = {
        "version_id": version_id
    }
    Brake_Config_Version_Api().remove_version(**params)
