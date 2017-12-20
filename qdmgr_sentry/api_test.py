# --*-- coding:utf8 --*--
from test.brake_password_api_test import test_password
from apps.common.utils.redis_client import Redis_Client

rc = Redis_Client()


def test_brake_api():
    from test.brake_card_api_test import test_brake_card_api
    test_brake_card_api()

    from test.brake_machine_api_test import test_brake_machine_api
    test_brake_machine_api()

    from test.brake_version_api_test import test_brake_version_api
    test_brake_version_api()

    from test.brake_password_api_test import test_brake_password_api
    test_brake_password_api()

    from test.brake_pass_api_test import test_brake_pass_api
    test_brake_pass_api()

    from test.brake_alert_api_test import test_brake_alert_api
    test_brake_alert_api()

    from test.brake_log_api_test import test_brake_log_api
    test_brake_log_api()

    from test.brake_config_version_api_test import test_brake_config_version_api
    test_brake_config_version_api()

    from test.brake_configer_api_test import test_brake_configer_api
    test_brake_configer_api()

    from test.brake_machine_test_tool_api_test import test_brake_machine_test_tool_api
    test_brake_machine_test_tool_api()

    from test.brake_machine_test_tool_record_api_test import test_set_brake_machine_test_tool_record_list
    test_set_brake_machine_test_tool_record_list()


def test_basedata_api():
    from test.basedata_project_api_test import test_basedata_project_api
    test_basedata_project_api()

    from test.basedata_group_api_test import test_basedata_group_api
    test_basedata_group_api()

    from test.basedata_build_api_test import test_basedata_build_api
    test_basedata_build_api()

    from test.basedata_unit_api_test import test_basedata_unit_api
    test_basedata_unit_api()

    from test.basedata_apartment_api_test import test_basedata_apartment_api
    test_basedata_apartment_api()

    from test.basedata_bj_app_user_api_test import test_basedata_bj_app_user_api
    test_basedata_bj_app_user_api()


def test_user_api():
    from test.web_user_api_test import test_web_user_api
    test_web_user_api()


def test_password_api():
    test_password()


def test_sync_data():
    from apps.basedata.process.sync_bj_data_api import get_xml_data
    get_xml_data("1852.xml")


def dev_test():
    from apps.common.api.brake_api import Brake_Pass_Api
    import time
    Brake_Pass_Api().set_user_pass(int(time.time()), '112233445566', '4', '3433904730', None, rc)


def test_all():
    # test_sync_data()
    test_basedata_api()
    test_brake_api()
    test_user_api()
    test_password_api()
    # dev_test()
