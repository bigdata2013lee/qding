# -*- coding: utf-8 -*-
import datetime
from apps.brake.classes.Brake_Password import Brake_Password
from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument
from mongoengine.fields import IntField, StringField, DateTimeField, ReferenceField, DictField
from apps.common.utils.sentry_date import get_day_datetime, get_datetime_by_timestamp


class Sentry_Visitor(Base_Class, DynamicDocument):
    '''
    @note: visitor_type  登记类型，0-App，1-电话/现场，2-临时
    '''
    brake_password = ReferenceField(Brake_Password, default=None)
    _brake_password = DictField(default={
        "valid_num": 0,
        "password": "",
        "start_time": None,
        "end_time": None,
        "bj_app_user": {
            "outer_app_user_id": "",
            "app_user_id": 0,
            "phone": "",
        },
        "apartment": {
            "province": "",
            "city": "",
            "project": "",
            "group": "",
            "build": "",
            "unit": "",
            "room": "",
            "outer_project_id": "",
            "outer_group_id": "",
            "outer_build_id": "",
            "outer_room_id": "",
            "project_id": None,
            "group_id": None,
            "build_id": None,
            "unit_id": None,
        }
    })
    visitor_type = StringField(default="1")  # "1":密码
    coming = StringField(default="0")  # "0"-未来,"1"-来了
    name = StringField(default="")
    reason = StringField(default="")
    visitor_cnt = IntField(default=1)
    start_time = DateTimeField(default=datetime.datetime.now())
    end_time = DateTimeField(default=datetime.datetime.now())

    meta = {'collection': 'sentry_visitor'}

    def get_count(self, project_id, unit_id):
        raw_query = {
            '_brake_password.apartment.project_id': project_id,
            '_brake_password.apartment.unit_id': unit_id,
            'created_time': {'$gt': get_day_datetime(), '$lt': get_day_datetime(1)},
            'status': '1'
        }
        return Sentry_Visitor.objects(__raw__=raw_query).count()

    def set__brake_password(self):
        self._brake_password = {
            "valid_num": self.brake_password.valid_num,
            "password": self.brake_password.password,
            "start_time": self.brake_password.start_time,
            "end_time": self.brake_password.end_time,
            "bj_app_user": {
                "outer_app_user_id": self.brake_password.bj_app_user.outer_app_user_id,
                "app_user_id": self.brake_password.bj_app_user.app_user_id,
                "phone": self.brake_password.bj_app_user.phone,
            },
            "apartment": {
                "province": self.brake_password.apartment.province,
                "city": self.brake_password.apartment.city,
                "project": self.brake_password.apartment.project,
                "group": self.brake_password.apartment.group,
                "build": self.brake_password.apartment.build,
                "unit": self.brake_password.apartment.unit,
                "room": self.brake_password.apartment.room,
                "outer_project_id": self.brake_password.apartment.outer_project_id,
                "outer_group_id": self.brake_password.apartment.outer_group_id,
                "outer_build_id": self.brake_password.apartment.outer_build_id,
                "outer_room_id": self.brake_password.apartment.outer_room_id,
                "project_id": self.brake_password.apartment.project_id,
                "group_id": self.brake_password.apartment.group_id,
                "build_id": self.brake_password.apartment.build_id,
                "unit_id": self.brake_password.apartment.unit_id,
            }
        }

    def get_visitor_list(self, province=None, city=None, project=None,
                         group=None, build=None, unit=None, room=None,
                         page_size=30, page_no=1, start_time=None, end_time=None,
                         coming=None):
        raw_query = {
            'status': '1'
        }
        d = {
            "province": province,
            "city": city,
            "project": project,
            "group": group,
            "build": build,
            "unit": unit,
            "room": room,
        }
        for k,v in d.items():
            if not v: continue
            raw_query.update({
                "_brake_password.apartment.%s" % k: v
            })
        if start_time and end_time:
            start_time = get_datetime_by_timestamp(timestamp=int(start_time), index=-1)
            end_time = get_datetime_by_timestamp(timestamp=int(end_time), index=1)
            raw_query.update(
                {
                    'created_time': {"$gt": start_time},
                    'created_time': {"$lt": end_time},
                }
            )
        if coming in ['0', '1']:
            raw_query.update(
                {
                    "coming": coming
                }
            )
        if int(page_size):
            return Sentry_Visitor.objects(__raw__=raw_query).order_by("-created_time").skip(
                (page_no - 1) * page_size).limit(page_size)
        return Sentry_Visitor.objects(__raw__=raw_query).order_by("-created_time")

    def get_visitor_by_password(self):
        return Sentry_Visitor.objects(brake_password=self.brake_password).first()

    def get_visitor_info(self):
        build = self._brake_password['apartment']['build']
        unit = self._brake_password['apartment']['unit']
        room = self._brake_password['apartment']['room']
        status = getattr(self, "coming", "0") or "0"
        valid_num = self._brake_password["valid_num"]
        ret = {
            "city": self._brake_password['apartment']['city'],
            "community": self._brake_password['apartment']['project'],
            "room": "%s栋%s单元%s" % (build, unit, room),
            "phone": self._brake_password['bj_app_user']['phone'],
            "start_time": self._brake_password['start_time'],
            "end_time": self._brake_password['end_time'],
            "reason": getattr(self, "reason", "") or "",
            "status": status,
            "dump_status": "是" if status == "1" else "否",
            "valid_num": valid_num,
            "dump_valid_num": "%s次" % valid_num if valid_num != -1 else "无限次",
        }
        return ret
