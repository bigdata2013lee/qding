# -*- coding: utf-8 -*-
import pickle
import re
from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument
from mongoengine.fields import StringField, DictField
from apps.brake.api.Pass_Data_Init_Processor import Pass_Data_Init_Processor
from apps.brake.api.Pass_Data_Status_Processor import Pass_Data_Status_Processor
from apps.brake.api.Pass_Data_Sync_Processor import Pass_Data_Sync_Processor
from apps.common.utils.sentry_date import get_datetime_by_timestamp, get_str_time_by_timestamp, get_timestamp_by_str_day
from apps.common.utils.redis_client import rc
from apps.common.utils.qd_decorator import method_set_rds


class Brake_Pass(Base_Class, DynamicDocument):
    pass_type = StringField(default="0")  # 0-bluetooth, 1-WiFi，2-password，4-card, 5-exit button 6-hal warning
    user_type = StringField(default="0")  # 0-resident, 1-visitor
    pass_info = DictField(default={
        "brake_machine": {
            "position": {},
            "position_str": "",
            "gate_info": {},
            "mac": "",
        },
        "app_user": {
            "phone": "",
            "outer_app_user_id": "",
            "app_user_id": None,
            "room_data_list": [],
        },
        "brake_password": {
            "password_obj": None,
            "password": "",
            "apartment": {},
        },
        "brake_card": {
            "card_no": None,
            "card_owner": {},
        },
    })
    meta = {"collection": "brake_pass"}

    def get_user_identify(self):
        if self.pass_type == '4':
            return self.pass_info['brake_card'].get("card_no", "")
        return self.pass_info['app_user'].get("phone", "")

    def get_position_str(self):
        position_str = ""
        position = self.pass_info['brake_machine']['position']
        gate_info = self.pass_info['brake_machine']['gate_info']
        level = int(position.get("level", 0) or 0)
        if not level:
            return position_str
        for project in position.get("project_list", []) or []:
            position_str = "%s%s" % (position_str, project.get("project", "") or "")
            if level == 2:
                continue
            for group in project.get("group_list", []) or []:
                position_str = "%s%s" % (position_str, group.get("group", "") or "")
                if level == 3:
                    continue
                for build in group.get("build_list", []) or []:
                    build_name = build.get("build", "") or ""
                    build_re = re.compile('.*栋$')
                    if not build_re.match(build_name): build_name = u"%s栋" % build_name
                    position_str = "%s%s" % (position_str, build_name)
                    if level == 4:
                        continue
                    for unit in build.get("unit_list", []) or []:
                        unit_re = re.compile('.*单元$')
                        if not unit_re.match(unit): unit = u"%s单元" % str(unit)
                        position_str = "%s%s" % (position_str, unit)
        gate_name = gate_info.get("gate_name", "") or ""
        direction = gate_info.get("direction", "I") or "I"
        position_str = "%s%s入" % (position_str, gate_name)
        if direction == "O":
            position_str = "%s%s出" % (position_str, gate_name)
        return position_str

    def get_pass_type_str(self):
        if self.pass_type == '0':
            return "蓝牙"
        if self.pass_type == '1':
            return "wifi"
        if self.pass_type == '2':
            return "密码"
        if self.pass_type == '4':
            return "卡"
        return ""

    def get_user_type(self):
        user_type = getattr(self, "user_type", "") or ""
        if user_type:
            return int(user_type)
        else:
            return 0

    def get_created_time(self):
        return getattr(self, "created_time", "") or ""

    def set_pass(self, result, apartment, brake_obj, sentry_visitor):
        init_processor = Pass_Data_Init_Processor()
        status_processor = Pass_Data_Status_Processor()
        init_processor.set_processor(status_processor)
        sync_processor = Pass_Data_Sync_Processor()
        status_processor.set_processor(sync_processor)
        init_processor.hand_request(self, result, apartment, brake_obj, sentry_visitor)

    def get_brake_pass_info(self):
        brake_machine = self.pass_info['brake_machine']
        position = brake_machine.get("position", {})
        project_list = position.get("project_list", []) or []
        user_type = self.get_user_type()
        created_time = self.get_created_time()
        gate_info = brake_machine.get("gate_info", {})
        direction = gate_info.get("direction", "I")
        pass_info = {
            'phone': self.get_user_identify(),
            'user_type': user_type,
            'pass_type': self.pass_type,
            "dump_user_type": self.get_pass_type_str(),
            'direction': direction,
            "created_time": int(created_time.timestamp()) if created_time else 0,
            "created_time_str": created_time,
            "position": brake_machine.get("position_str", ""),
            "mac": brake_machine.get("mac", ""),
            "province": position.get("province", "") or "",
            "city": position.get("city", "") or "",
            "community": project_list[0].get("project", "") if project_list else "",
        }
        return pass_info

    def get_project_day_pass_count(self, province, city, project, start_day, end_day):
        day_pass_count_list = []
        while start_day < end_day:
            ret = {'cummunity_gate_pass_num': 0, 'unit_gate_pass_num': 0,
                   'day': get_str_time_by_timestamp(timestamp=start_day, str_format="%Y-%m-%d")}
            day = get_str_time_by_timestamp(start_day, str_format="%Y-%m-%d")
            keys = "%s#%s#%s#%s" % (day, province, city, project)
            redis_ret = rc.get(keys)
            if redis_ret:
                ret = pickle.loads(redis_ret)
            else:
                project_pass_count_dict = {"province": province, "city": city, "project": project, "day": day}
                value = pickle.dumps({"update_project_pass_count": project_pass_count_dict})
                rc.sadd("update_process", value)
            day_pass_count_list.append(ret)
            start_day += 24 * 3600
        return day_pass_count_list

    @classmethod
    def set_project_day_pass_count(cls, province, city, project, day):
        ret = {'cummunity_gate_pass_num': 0, 'unit_gate_pass_num': 0, 'day': day}
        day = get_timestamp_by_str_day(day)
        start_time = get_datetime_by_timestamp(timestamp=day, index=0)
        end_time = get_datetime_by_timestamp(timestamp=day, index=1)
        raw_query = {
            'pass_info.brake_machine.position.province': province,
            'pass_info.brake_machine.position.city': city,
            'pass_info.brake_machine.position.project_list.project': project,
            'created_time': {"$gt": start_time, "$lt": end_time}
        }
        brake_pass_list = Brake_Pass.objects(__raw__=raw_query)
        for brake_pass in brake_pass_list:
            position = brake_pass.pass_info['brake_machine'].get("position", {})
            level = int(position.get("level", 0) or 0)
            if level != 5:
                ret['cummunity_gate_pass_num'] += 1
            else:
                ret['unit_gate_pass_num'] += 1
        return ret

    @classmethod
    @method_set_rds(60)
    def get_unique_pass(cls, created_time, mac):
        raw_query = {
            "created_time": created_time,
            "pass_info.brake_machine.mac": mac
        }
        if Brake_Pass.objects(__raw__=raw_query).first(): return True
        return None

    def get_all_pass(self):
        return Brake_Pass.objects(status="1")

    def get_brake_pass_list_by_position(self, province=None, city=None, project=None, group=None, build=None,
                                        unit=None, pass_type=None, user_type=None, brake_type=None,
                                        start_time=None, end_time=None, page_size=0, page_no=1):
        raw_query = {"status": "1"}
        if province:
            raw_query.update({
                'pass_info.brake_machine.position.province': province,
            })
        if city:
            raw_query.update({
                'pass_info.brake_machine.position.city': city,
            })
        if project:
            raw_query.update({
                'pass_info.brake_machine.position.project_list.project': project,
            })
        if group:
            raw_query.update({
                'pass_info.brake_machine.position.project_list.group_list.group': group,
            })
        if build:
            raw_query.update({
                'pass_info.brake_machine.position.project_list.group_list.build_list.build': build,
            })
        if unit:
            raw_query.update({
                'pass_info.brake_machine.position.project_list.group_list.build_list.unit_list': unit,
            })
        if brake_type == 2:
            raw_query.update({
                'pass_info.brake_machine.position.level': 2,
            })
        elif brake_type == 3:
            raw_query.update({
                'pass_info.brake_machine.position.level': {"$ne": 2},
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
        if pass_type in ['0', '1', '2', '4']:
            raw_query.update({
                "pass_type": pass_type
            })
        if user_type:
            raw_query.update({
                "user_type": user_type
            })
        if page_size:
            skip = (page_no - 1) * page_size
            return Brake_Pass.objects(__raw__=raw_query).order_by("-created_time").skip(skip).limit(page_size)
        return Brake_Pass.objects(__raw__=raw_query).order_by("-created_time")

    @classmethod
    def get_brake_pass_list_by_phone(cls, phone, page_no=1, page_size=30, sorted_field='updated_time'):
        raw_query = {
            "pass_info.app_user.phone": phone,
        }
        if page_size:
            skip = (page_no - 1) * page_size
            return Brake_Pass.objects(__raw__=raw_query).order_by("-created_time").order_by(sorted_field).skip(
                skip).limit(page_size)
        return Brake_Pass.objects(__raw__=raw_query).order_by(sorted_field)

    def get_brake_pass_list_by_outer_app_user_id(self, outer_app_user_id, page_no=1, page_size=30):
        raw_query = {
            "pass_info.app_user.outer_app_user_id": outer_app_user_id,
        }
        if page_size:
            skip = (page_no - 1) * page_size
            return Brake_Pass.objects(__raw__=raw_query).order_by("-created_time").skip(skip).limit(page_size)
        return Brake_Pass.objects(__raw__=raw_query)

    @classmethod
    def get_brake_pass_list_by_mac(cls, mac, page_no=1, page_size=30):
        raw_query = {
            "pass_info.brake_machine.mac": mac,
        }
        if page_size:
            skip = (page_no - 1) * page_size
            return Brake_Pass.objects(__raw__=raw_query).order_by("-created_time").skip(skip).limit(page_size)
        return Brake_Pass.objects(__raw__=raw_query)

    @classmethod
    def get_brake_pass_list_by_card_no(cls, card_no, page_no=1, page_size=30):
        raw_query = {
            "pass_info.brake_card.card_no": card_no,
        }
        if page_size:
            skip = (page_no - 1) * page_size
            return Brake_Pass.objects(__raw__=raw_query).order_by("-created_time").skip(skip).limit(page_size)
        return Brake_Pass.objects(__raw__=raw_query)



