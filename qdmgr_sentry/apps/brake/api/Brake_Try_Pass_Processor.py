# -*- coding:utf8 -*-
import os, pickle, datetime, json
from apps.common.utils.sentry_date import get_str_day_by_datetime
from apps.common.utils.redis_client import rc
from settings.const import CONST
from apps.common.utils.request_api import request_bj_server
from apps.basedata.classes.Basedata_BJ_App_User import Basedata_BJ_App_User


class Brake_Try_Pass_Processor(object):
    def __init__(self, pass_user=None, pass_device=None, pass_medium=None, pass_info=None, sentry_visitor=None):
        self.pass_user = pass_user
        self.pass_device = pass_device
        self.pass_medium = pass_medium
        self.pass_info = pass_info
        self.sentry_visitor = sentry_visitor

    def set_pass_data(self, brake_try_pass=None):
        brake_try_pass.pass_device = self.pass_device
        brake_try_pass.pass_info = self.pass_info

        if brake_try_pass.pass_type in ['0', '1']:
            return self._set_app_pass_data(brake_try_pass)
        elif brake_try_pass.pass_type in ['2', '9']:
            return self._set_password_pass_data(brake_try_pass)
        elif brake_try_pass.pass_type in ['4', '10']:
            return self._set_card_pass_data(brake_try_pass)
        elif brake_try_pass.pass_type in ['5', '6', '7', '11']:
            return self._set_other_pass_data(brake_try_pass)

        return True, ''

    def _set_app_pass_data(self, brake_try_pass):
        self.pass_user.update({'user_type': '0'})
        brake_try_pass.pass_user = self.pass_user
        brake_try_pass.pass_medium = {}
        return True, ''

    def _set_password_pass_data(self, brake_try_pass):
        brake_try_pass.pass_user = {'user_type': '1'}
        bj_app_user = getattr(self.pass_medium, "bj_app_user", None) or None
        if not bj_app_user:
            return False, "Password_Brake_Pass_Observer: not get app user"
        if self.pass_medium.valid_num > 0:
            self.pass_medium.valid_num -= 1
            self.pass_medium.save()

        self.sentry_visitor.coming = "1"
        self.sentry_visitor.save()

        brake_try_pass.pass_medium = {
            "app_user": Basedata_BJ_App_User.get_app_info_for_pass(bj_app_user),
            "brake_password": {
                "password": self.pass_medium.password,
                "apartment": self.pass_medium.apartment_dict,
                'request_time': self.pass_medium.created_time,
            }
        }
        return True, ''

    def _set_card_pass_data(self, brake_try_pass):
        card_owner = self.pass_medium.get("card_owner", None) if self.pass_medium else None
        card_no = self.pass_medium.get("card_no", None) if self.pass_medium else None
        card_area = self.pass_medium.get("card_area", None) if self.pass_medium else None

        phone = card_owner.get('phone', '') if card_owner else ''
        name = card_owner.get('name', '') if card_owner else ''
        gender = card_owner.get('gender', '') if card_owner else ''

        brake_try_pass.pass_user = {
            'user_type': '0',
            'phone': phone,
            'name': name,
            'gender': gender,
        }

        brake_try_pass.pass_medium = {
            'brake_card': {
                'card_no': card_no,
                'card_area': card_area,
            }
        }

        return True, ''

    def _set_other_pass_data(self, brake_try_pass):
        self.pass_user.update({'user_type': '0'})
        brake_try_pass.pass_user = self.pass_user
        brake_try_pass.pass_medium = {}

        return True, ''

    @classmethod
    def save_pass_data(cls, brake_try_pass, brake_machine, sentry_visitor_obj, result):
        if brake_try_pass.get_unique_pass(created_time=brake_try_pass.created_time, mac=brake_machine.mac):
            result['msg'] = 'Brake_Try_Pass_Processor: 同一闸机同一秒只允许存在一条通行记录'
            result['data']['flag'] = 'N'
        else:
            brake_try_pass.save()

        if result['data']['flag'] == 'Y' and brake_try_pass.pass_type in ['0', '1', '2', '4'] \
                and brake_try_pass.pass_info['pass_code'] == 0:
            cls._save_pass_data_status(brake_try_pass, brake_machine)
            cls._save_pass_data_to_sync(brake_try_pass, sentry_visitor_obj)

    @classmethod
    def _save_pass_data_status(cls, brake_try_pass, brake_machine):
        pass_time = int(brake_machine.updated_time.timestamp())
        created_time = int(brake_try_pass.created_time.timestamp())
        if pass_time < created_time: pass_time = created_time
        brake_machine.updated_time = datetime.datetime.fromtimestamp(pass_time)
        brake_machine.save()

        day = get_str_day_by_datetime(brake_try_pass.created_time)
        position = brake_try_pass.pass_device['position']
        province = position['province']
        city = position['city']
        project = position['project_list'][0]['project']
        keys = "%s#%s#%s#%s" % (day, province, city, project)
        redis_ret = rc.get(keys)
        if redis_ret:
            ret = pickle.loads(redis_ret)
            level = brake_machine.position.get("level", 0) or 0
            if level in [2, 3]:
                ret['cummunity_gate_pass_num'] += 1
            elif level in [4, 5]:
                ret['unit_gate_pass_num'] += 1
        else:
            ret = brake_try_pass.set_project_day_pass_count(province, city, project, day)
        rc.set(keys, pickle.dumps(ret))

    @classmethod
    def _save_pass_data_to_sync(cls, brake_try_pass, sentry_visitor_obj):
        ret = {}
        pass_user = brake_try_pass.pass_user
        if brake_try_pass.pass_type == '2':
            pass_user = brake_try_pass.pass_medium['app_user']

        pass_device = brake_try_pass.pass_device
        brake_card = getattr(brake_try_pass, 'brake_card', {})

        position = pass_device['position']
        project = position['project_list'][0].get('project', '') if position['project_list'] else ''
        outer_project_id = position['project_list'][0].get('outer_project_id', '') if position['project_list'] else ''

        ret['unique_id'] = "%s%s" % (pass_device['mac'], int(brake_try_pass.created_time.timestamp()))
        room_data_list = [] if not pass_user else pass_user.get("room_data_list", [])
        user_type = '0' if len(room_data_list) == 0 else room_data_list[0].get('role', '0') or '0'
        ret['user_type'] = user_type
        ret['project_id'] = outer_project_id
        ret['project_name'] = project
        ret['room_id'] = room_data_list[0].get('outer_room_id', '') if room_data_list else ""
        ret['room_name'] = room_data_list[0].get('room', '') if room_data_list else ""
        ret['user_id'] = pass_user.get("outer_app_user_id", "")
        ret['mobile'] = pass_user.get("phone", "")
        ret['pass_time'] = int(brake_try_pass.created_time.timestamp())
        ret['pass_type'] = pass_device['gate_info'].get("direction", "I")
        ret['pass_position'] = pass_device['position_str']
        ret['pass_media'] = getattr(brake_try_pass, "pass_type", 0) or 0
        ret['card_no'] = brake_card.get("card_no", "")
        method_url = 'syncPassLog?body={"uqineId":"%s","projectId":"%s"' % (ret['unique_id'], ret['project_id'])
        method_url = "%s%s" % (method_url, ',"passType":"%s","roomId":"%s"' % (ret['pass_type'], ret['room_id']))
        method_url = "%s%s" % (method_url, ',"passMedia":"%s", "cardNo":"%s"' % (ret['pass_media'], ret['card_no']))
        method_url = "%s%s" % (
            method_url, ',"userId":"%s","passPosition":"%s"' % (ret['user_id'], ret['pass_position']))
        method_url = "%s%s" % (
            method_url, ',"roomName":"%s","projectName":"%s"' % (ret['room_name'], ret['project_name']))
        if brake_try_pass.pass_type == '2':
            ret['created_time'] = int(sentry_visitor_obj.created_time.timestamp())
            ret['reason'] = sentry_visitor_obj.reason
            ret['user_type'] = '1'
            method_url = "%s%s" % (
                method_url, ',"reason":"%s","createTime":"%s"' % (ret['reason'], ret['created_time']))
        method_url = "%s%s" % (method_url, ',"passTime":"%s","mobile":"%s","userType":"%s"}' % (
            ret['pass_time'], ret['mobile'], ret['user_type']))
        method_url = method_url.replace("#", "")
        request_bj_server(method_url=method_url, method_params={}, post_flag=False)

        # pass_data = json.dumps(ret, sort_keys=True)
        # rc.sadd('user_pass_to_sync_set', pass_data)
        # if rc.cnn.scard('user_pass_to_sync_set') >= 1:
        #     pass_data_list = rc.cnn.smembers('user_pass_to_sync_set')
        #     cls.write_file(pass_data_list)
        #     for data in pass_data_list:
        #         rc.cnn.srem('user_pass_to_sync_set', data)

    @classmethod
    def write_file(cls, data_list):
        str_day = get_str_day_by_datetime(datetime.datetime.now(), str_format='%Y%m%d')
        pass_data_dir = CONST['static']['brake_pass_dir']
        if not os.path.exists(pass_data_dir):
            os.makedirs(pass_data_dir)
        file_name = '%s%s.txt' % (pass_data_dir, str_day)
        file_obj = open(file_name, 'a+')
        data_list = [data.decode('utf8') + '\n' for data in data_list]
        file_obj.writelines(data_list)
        file_obj.close()














