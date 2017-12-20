# -*- coding: utf-8 -*-
import re
import pickle
from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument
from mongoengine.fields import StringField, DictField
from apps.common.utils.sentry_date import get_datetime_by_timestamp, get_timestamp_by_str_day
from apps.common.utils.qd_decorator import method_set_rds
from apps.brake.api.Brake_Try_Pass_Processor import Brake_Try_Pass_Processor

PASS_TYPE_DICT = {
    '0': '蓝牙',
    '1': 'WiFi',
    '2': '密码',
    '4': '卡',
    '6': '拆除',
    '9': '密码',
    '10': '卡',
    '11': '调试',
}


class Brake_Try_Pass(Base_Class, DynamicDocument):
    pass_type = StringField(default="0")  # 0-bluetooth, 1-WiFi，2-password，4-card, 5-exit button 6-hal warning 9-password failed 10-card failed 11-config
    pass_user = DictField(default={
        "user_type": "", # 0-resident, 1-visitor
        "outer_member_id": "",
        "outer_app_user_id": "",
        "app_user_id": None,
        "phone": "",
        "gender": "",
        "name": "",
    })
    pass_device = DictField(default={
        "position": {},
        "position_str": "",
        "gate_info": {},
        "mac": "",
    })
    pass_medium = DictField(default={
        "brake_password": {
            "password": "",
            "apartment": {},
            "request_time": None,
        },
        "brake_card": {
            "enc_card_no":None,
            "card_no": None,
            "card_area": [],
        },
    })
    pass_info = DictField(default={
        "pass_mode": None, #100-手动, 101-自动
        "pass_code": None,
    })

    meta = {"collection": "brake_try_pass"}

    @classmethod
    @method_set_rds(60)
    def get_unique_pass(cls, created_time, mac):
        raw_query = {
            "created_time": created_time,
            "pass_device.mac": mac
        }
        if Brake_Try_Pass.objects(__raw__=raw_query).first(): return True
        return None

    @classmethod
    def set_project_day_pass_count(cls, province, city, project, day):
        ret = {'cummunity_gate_pass_num': 0, 'unit_gate_pass_num': 0, 'day': day}
        day = get_timestamp_by_str_day(day)
        start_time = get_datetime_by_timestamp(timestamp=day, index=0)
        end_time = get_datetime_by_timestamp(timestamp=day, index=1)
        raw_query = {
            'pass_device.position.province': province,
            'pass_device.position.city': city,
            'pass_device.position.project_list.project': project,
            'created_time': {"$gt": start_time, "$lt": end_time}
        }
        brake_pass_list = Brake_Try_Pass.objects(__raw__=raw_query)
        for brake_pass in brake_pass_list:
            position = brake_pass.pass_device.get("position", {})
            level = int(position.get("level", 0) or 0)
            if level != 5:
                ret['cummunity_gate_pass_num'] += 1
            else:
                ret['unit_gate_pass_num'] += 1
        return ret

    def save_data(self, brake_machine, sentry_visitor, result):
        Brake_Try_Pass_Processor.save_pass_data(self, brake_machine, sentry_visitor, result)

    def get_user_type(self):
        user_type = self.pass_user.get('user_type', '0')
        if user_type:
            return int(user_type)
        else:
            return 0

    def get_user_identify(self):
        if self.pass_type in ['2', '9']:
            return self.pass_medium['app_user'].get("phone", "")
        elif self.pass_type in ['4', '10']:
            return self.pass_medium['brake_card'].get("card_no", "")
        return self.pass_user.get("phone", "")

    def get_pass_type_str(self):
        return PASS_TYPE_DICT.get(self.pass_type, '')

    def get_created_time(self):
        return getattr(self, "created_time", "") or ""

    def get_brake_try_pass_info(self):
        position = self.pass_device.get("position", {})
        project_list = position.get("project_list", []) or []
        user_type = self.get_user_type()
        created_time = self.get_created_time()
        gate_info = self.pass_device.get("gate_info", {})
        direction = gate_info.get("direction", "I")
        pass_info = {
            'phone': self.get_user_identify(),
            'user_type': user_type,
            'pass_type': self.pass_type,
            "dump_user_type": self.get_pass_type_str(),
            'direction': direction,
            "created_time": int(created_time.timestamp()) if created_time else 0,
            "created_time_str": created_time,
            "position": self.pass_device.get("position_str", ""),
            "mac": self.pass_device.get("mac", ""),
            "province": position.get("province", "") or "",
            "city": position.get("city", "") or "",
            "community": project_list[0].get("project", "") if project_list else "",
        }
        return pass_info

    @classmethod
    def get_all_pass_count(cls):
        raw_query = {
            'pass_type': {'$nin': ['6', '11']},
            'status': '1',
        }
        return Brake_Try_Pass.objects(__raw__=raw_query).count()

    @classmethod
    def get_brake_try_pass_list_by_position(cls, province=None, city=None, project=None, group=None, build=None,
                                        unit=None, pass_type=None, user_type=None, brake_type=None,
                                        start_time=None, end_time=None, page_size=0, page_no=1):
        raw_query = {
            "status": "1",
            "pass_info.pass_code": 0,
        }
        if province:
            raw_query.update({
                'pass_device.position.province': province,
            })
        if city:
            raw_query.update({
                'pass_device.position.city': city,
            })
        if project:
            raw_query.update({
                'pass_device.position.project_list.project': project,
            })
        if group:
            raw_query.update({
                'pass_device.position.project_list.group_list.group': group,
            })
        if build:
            raw_query.update({
                'pass_device.position.project_list.group_list.build_list.build': build,
            })
        if unit:
            raw_query.update({
                'pass_device.position.project_list.group_list.build_list.unit_list': unit,
            })
        if brake_type == 2:
            raw_query.update({
                'pass_device.position.level': 2,
            })
        elif brake_type == 3:
            raw_query.update({
                'pass_device.position.level': {"$ne": 2},
            })
        if start_time and end_time:
            start_time = get_datetime_by_timestamp(int(start_time))
            end_time = get_datetime_by_timestamp(int(end_time), index=1)
            raw_query.update({
                "created_time": {
                    "$gt": start_time,
                    "$lt": end_time,
                }
            })
        if pass_type in ['0', '1', '2', '4', '6', '11']:
            raw_query.update({
                "pass_type": pass_type,
            })

        if user_type:
            raw_query.update({
                "pass_user.user_type": user_type,
            })
        if page_size:
            skip = (page_no - 1) * page_size
            return Brake_Try_Pass.objects(__raw__=raw_query).order_by("-created_time").skip(skip).limit(page_size)
        return Brake_Try_Pass.objects(__raw__=raw_query).order_by("-created_time")

    @classmethod
    def get_brake_try_pass_list_by_phone(cls, phone, page_no=1, page_size=30, sorted_field='updated_time'):
        raw_query = {
            "pass_user.phone": phone,
        }
        if page_size:
            skip = (page_no - 1) * page_size
            return Brake_Try_Pass.objects(__raw__=raw_query).order_by("-created_time").order_by(sorted_field).skip(
                skip).limit(page_size)
        return Brake_Try_Pass.objects(__raw__=raw_query).order_by(sorted_field)

    @classmethod
    def get_brake_try_pass_list_by_card_no(cls, card_no, page_no=1, page_size=30):
        raw_query = {
            "pass_medium.brake_card.card_no": card_no,
        }
        if page_size:
            skip = (page_no - 1) * page_size
            return Brake_Try_Pass.objects(__raw__=raw_query).order_by("-created_time").skip(skip).limit(page_size)
        return Brake_Try_Pass.objects(__raw__=raw_query)

    @classmethod
    def get_phone_from_app_user_id(cls, app_user_id):
        cvt_dict = {
            0: '13',
            1: '15',
            2: '17',
            3: '18',
        }
        if int(app_user_id) == int(0xffffffff):
            return '12345678901'
        first_num = (int(app_user_id) & (0x3 << 30)) >> 30
        last_num = int(app_user_id) & 0x3fffffff
        return cvt_dict[first_num] + str(last_num)

    @classmethod
    def get_failed_brake_try_pass_list(cls,province=None, city=None, project=None, group=None, build=None,
                                  unit=None, mac=None, pass_type="", phone=None,  start_time=None,
                                  end_time=None, page_size='30', page_no='1'):
        raw_query = {
            "status": "1",
            'pass_info.pass_code': {'$ne': 0},
        }
        if province:
            raw_query.update({
                'pass_device.position.province': province,
            })
        if city:
            raw_query.update({
                'pass_device.position.city': city,
            })
        if project:
            raw_query.update({
                'pass_device.position.project_list.project': project,
            })
        if group:
            raw_query.update({
                'pass_device.position.project_list.group_list.group': group,
            })
        if build:
            raw_query.update({
                'pass_device.position.project_list.group_list.build_list.build': build,
            })
        if unit:
            raw_query.update({
                'pass_device.position.project_list.group_list.build_list.unit_list': unit,
            })
        if mac:
            raw_query.update({
                'pass_device.mac': mac,
            })

        if pass_type in ['0', '1', '9', '10']:
            raw_query.update({
                'pass_type': pass_type,

            })

        if phone:
            if pass_type in ['0', '1']:
                raw_query.update({
                    'pass_user.phone': phone,
                })
            elif pass_type == '9':
                raw_query.update({
                    'pass_medium.app_user.phone': phone,
                })
            elif pass_type == '10':
                raw_query.update({
                    'pass_medium.brake_card.card_no': int(phone),
                })

        if start_time and end_time:
            start_time = get_datetime_by_timestamp(int(start_time))
            end_time = get_datetime_by_timestamp(int(end_time), index=1)
            raw_query.update({
                "created_time": {
                    "$gt": start_time,
                    "$lt": end_time,
                }
            })
        elif start_time:
            start_time = get_datetime_by_timestamp(int(start_time))
            raw_query.update({
                "created_time": {"$gt": start_time}
            })
        elif end_time:
            end_time = get_datetime_by_timestamp(int(end_time), index=1)
            raw_query.update({
                "created_time": {"$lt": end_time}
            })

        if page_size:
            skip = (page_no - 1) * page_size
            return Brake_Try_Pass.objects(__raw__=raw_query).order_by("-created_time").skip(skip).limit(page_size)
        return Brake_Try_Pass.objects(__raw__=raw_query).order_by("-created_time")
