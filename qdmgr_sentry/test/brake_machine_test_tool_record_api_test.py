# --*-- coding:utf8 --*--

from apps.common.api.brake_api import Brake_Machine_Test_Tool_Record_Api


def test_brake_machine_test_tool_record_api():
    test_set_brake_machine_test_tool_record_list()


def test_set_brake_machine_test_tool_record_list():
    params = {
        "record_list": '[{"mac":"123123123","app_user_id":"1212323","created_time":"1234567890","open_success":1,"scan_time":123,"connect_time":123,"get_service_time":123,"reach_signal_strength_time":123,"send_data_time":123,"get_result_time":123,"total_time":123}]',
        "phone_info": '{"model":"123","os_version":""}',
    }
    Brake_Machine_Test_Tool_Record_Api().set_brake_machine_test_tool_record_list(**params)
