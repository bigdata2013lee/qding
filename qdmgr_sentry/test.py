# --*-- coding:utf8 --*--
'''
cd /data/qding/qdmgr_sentry;ps -ef|grep python|grep -v grep|awk '{print $2}'|xargs sudo kill -9;ps -ef|grep uwsgi|grep -v grep|awk '{print $2}'|xargs sudo kill -9;sudo bash scripts/sentry.sh start
'''

import os, time
from mongoengine import connect
from settings.const import CONST



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.default")
connect("qdmgr_sentry", host="mongodb://%s/%s" % (CONST['mongodb']['host'], CONST['mongodb']['db']),
        port=CONST['mongodb']['port'], connect=False)

from apps.common.api import brake_api, basedata_api

# print('get_app_user_bind_room_list', basedata_api.Basedata_Bj_App_User_Api().get_app_user_bind_room_list('18188621491'))
# print('\n------------------\n')
# print('get_app_user_bind_door_list', basedata_api.Basedata_Bj_App_User_Api().get_app_user_bind_door_list('18188621491'))
# print('\n------------------\n')
# print('get_app_user_can_open_door', basedata_api.Basedata_Bj_App_User_Api().get_app_user_can_open_door('18188621491'))
# print('\n------------------\n')
# print('get_app_user_can_open_door_list', basedata_api.Basedata_Bj_App_User_Api().get_app_user_can_open_door_list('2c90805d50b820d90150d1b814c900ba'))
# print('\n------------------\n')
# print('set_app_user_can_open_door_list', basedata_api.Basedata_Bj_App_User_Api().set_app_user_can_open_door_list('18188621491', ['112233445566']))
# print('\n------------------\n')
# print('delete_app_user_can_open_door_list', basedata_api.Basedata_Bj_App_User_Api().delete_app_user_can_open_door_list('18188621491', ['112233445566']))
# print('\n------------------\n')
# print('set_app_user_can_pass_project', basedata_api.Basedata_Bj_App_User_Api().set_app_user_can_pass_project('1789', '18188621491', 'set_bind_door_list'))
# print('\n------------------\n')
# print('set_app_user_can_pass_project', basedata_api.Basedata_Bj_App_User_Api().set_app_user_can_pass_project('1852', '18188621491', 'delete_bind_door_list'))
# print('\n------------------\n')
# print('clear_app_user_can_open_door', basedata_api.Basedata_Bj_App_User_Api().clear_app_user_can_open_door(['18188621491']))
# print('\n------------------\n')
# print('get_app_user_id', basedata_api.Basedata_Bj_App_User_Api().get_app_user_id('2c90805d50b820d90150d1b814c900ba'))
# print('\n------------------\n')
# print('set_app_user_room_list', basedata_api.Basedata_Bj_App_User_Api().set_app_user_room_list('18188621491'))
# print('\n------------------\n')
# print('set_app_user_room_list_now', basedata_api.Basedata_Bj_App_User_Api().set_app_user_room_list_now('18188621491'))
# print('\n------------------\n')
print('get_app_user_by_filter', basedata_api.Basedata_Bj_App_User_Api().get_app_user_by_filter())

# print('\n------------------\n')
# print('add_password', brake_api.Brake_Password_Api().add_password(room_id='9151116111001', app_user_id='ac04d83278a011e58a30418611258576', reason='test'))
#
# print('\n------------------\n')
# print('sync_project_data', brake_api.Brake_Configer_Api().sync_project_data(province='中陲', city='中陲', project='千丁-嘉园'))

# print('\n------------------\n')
# print('get_card_info', brake_api.Brake_Card_Api().get_card_info(card_no='1229990890257536'))


# from apps.basedata.process import sync_bj_data_api
# sync_bj_data_api.test_get_xml_data('1879.xml')
# sync_bj_data_api.sync_project_data('1879')

# from apps.common.api.basedata_api import Basedata_Project_Api
# print(Basedata_Project_Api().find_project_by_name_from_bj("城"))

# user_pass_list=[
#         {"created_time": int(time.time()), "mac":"112233445566", "pass_type":"0", "app_user_id":"3206487522"},
#         {"created_time": int(time.time()), "mac":"112233445566", "pass_type":"1", "app_user_id":"3206487522"},
#         {"created_time": int(time.time()), "mac":"112233445566", "pass_type":"2", "app_user_id":"530106"},
#         {"created_time": int(time.time()), "mac":"112233445566", "pass_type":"4", "app_user_id":"2649654193"},
# ]
# print('\n------------------\n')
# print('set_user_pass_list', brake_api.Brake_Pass_Api().set_user_pass_list(user_pass_list=user_pass_list))

card_info = {"card_no":"045FEA62215280", "card_type":5,"card_validity":int(time.time())+10000000}
owner_info = {"name":"test","phone":"12345678901"}
room_id_list = [710420]
# print('\n------------------\n')
# print('app_get_write_no', brake_api.Brake_Card_Api().app_get_write_no(card_info=card_info, owner_info=owner_info, room_id_list=room_id_list))
#
#
# print('\n------------------\n')
# print('test_open_card', brake_api.Brake_Card_Api().test_open_card())

# print('\n------------------\n')
# print('get_black_and_white_list', brake_api.Brake_Card_Api().get_black_and_white_list("2c90805d50b820d90150d1b814c900ba"))
#
# print('\n------------------\n')
# print('get_black_and_white_list', brake_api.Brake_Card_Api().modify_card(card_id="591d61cec0d2071578db00be",status="3"))

# print('\n------------------\n')
# print('check_brake_firmware_version', basedata_api.Basedata_Bj_App_User_Api().check_brake_firmware_version(outer_app_user_id="2c90805d50b820d90150d1b814c900ba"))

# print('\n------------------\n')
# print('sync_project_data_by_id', brake_api.Brake_Configer_Api().sync_project_data_by_id(outer_project_id_list=['1879', '1789']))

