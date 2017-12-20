# -*- coding: utf-8 -*-
import logging

import datetime
import mongoengine

from apps.basedata.classes.Basedata_Apartment import Basedata_Apartment
from apps.brake.classes.Brake_Version import Brake_Version
from settings.const import CONST
from mongoengine.document import DynamicDocument
from apps.common.classes.Base_Class import Base_Class
from apps.common.utils.request_api import request_bj_server
from apps.brake.classes.Brake_Machine import Brake_Machine
from apps.common.utils.qd_decorator import method_set_rds
from mongoengine.fields import StringField, ListField, IntField, ReferenceField

logger = logging.getLogger('qding')


class Basedata_BJ_App_User(Base_Class, DynamicDocument):
    # status: 1-正常, 2-禁用门禁
    outer_member_id = StringField(default="")
    outer_app_user_id = StringField(default="")
    app_user_id = IntField(default=0)
    phone = StringField(default="")
    room_data_list = ListField(default=[])
    bind_door_list = ListField(ReferenceField(Brake_Machine, reverse_delete_rule=mongoengine.PULL), default=[])
    _bind_door_list = ListField(default=[])

    meta = {'collection': 'basedata_bj_app_user'}

    @classmethod
    @method_set_rds()
    def get_app_for_pass(cls, app_user_id):
        if isinstance(app_user_id, int):
            db_app_user = Basedata_BJ_App_User.objects(app_user_id=app_user_id).first()
        else:
            db_app_user = Basedata_BJ_App_User.objects(outer_app_user_id=app_user_id).first()
        if not db_app_user: return {}
        return cls.get_app_info_for_pass(db_app_user)

    @classmethod
    def get_app_info_for_pass(cls, db_app_user):
        return {
            "phone": db_app_user.phone,
            "outer_app_user_id": db_app_user.outer_app_user_id,
            "app_user_id": db_app_user.app_user_id,
            "room_data_list": db_app_user.room_data_list
        }

    def get__bind_door_list(self):
        return getattr(self, "_bind_door_list", []) or []

    def set_bind_door_list(self, bind_door_list):
        def _get_brake_info(brake_obj):
            return {
                "position": brake_obj.position,
                "level": brake_obj.position.get("level", 0),
                "mac": brake_obj.mac,
                "wifi_rssi": brake_obj.wifi_rssi,
                "bluetooth_rssi": brake_obj.bluetooth_rssi,
                "open_time": brake_obj.open_time,
                "version": brake_obj.firmware_version,
                "province": brake_obj.position['province'],
                "city": brake_obj.position['city'],
                "project": brake_obj.position['project_list'][0]['project'],
                "position_str": brake_obj.position_str,
                "gate_info": brake_obj.gate_info,
                "gate_name": brake_obj.gate_info.get("gate_name", ""),
                "direction": brake_obj.gate_info.get("direction", "I"),
                "updated_time": int(brake_obj.updated_time.timestamp()),
            }
        bind_door_list = list(set([str(brake.id) for brake in self.bind_door_list] + [brake['id'] for brake in bind_door_list]))
        self.bind_door_list = Brake_Machine.objects(id__in=bind_door_list)
        self._bind_door_list = [_get_brake_info(brake) for brake in self.bind_door_list]
        self.save()

    def delete_bind_door_list(self, delete_door_list):
        def _get_brake_info(brake_obj):
            return {
                "position": brake_obj.position,
                "mac": brake_obj.mac,
                "wifi_rssi": brake_obj.wifi_rssi,
                "bluetooth_rssi": brake_obj.bluetooth_rssi,
                "open_time": brake_obj.open_time,
                "version": brake_obj.firmware_version,
                "province": brake_obj.position['province'],
                "city": brake_obj.position['city'],
                "project": brake_obj.position['project_list'][0]['project'],
            }
        bind_door_list = list(set([str(brake.id) for brake in self.bind_door_list]))
        for door in delete_door_list:
            if door['id'] in bind_door_list:
                bind_door_list.remove(door['id'])
        self.bind_door_list = Brake_Machine.objects(id__in=bind_door_list)
        self._bind_door_list = [_get_brake_info(brake) for brake in self.bind_door_list]
        self.save()

    def set_app_user_id(self):
        from apps.common.utils.qd_encrypt import set_basedata_id
        input_msg = getattr(self, "outer_app_user_id", "") or ""
        self.app_user_id, count = set_basedata_id(input_msg, self.check_app_user_id_exits)
        return self.app_user_id

    def get_app_user_id(self):
        if not self.app_user_id:
            self.set_app_user_id()
            self.save()
        return self.app_user_id

    def check_app_user_id_exits(self, app_user_id):
        raw_query = {
            "outer_app_user_id": {"$ne": self.outer_app_user_id},
            "app_user_id": app_user_id
        }
        return Basedata_BJ_App_User.objects(__raw__=raw_query)

    def flush_app_user_info(self, app_user):
        self.outer_app_user_id = app_user.get("appUserId", None) or None
        if not self.outer_app_user_id:return None, "从北京服务器获取用户id失败"
        self.app_user_id = self.set_app_user_id()

        self.outer_member_id = app_user.get("memberId", None) or None

        self.phone = app_user.get("mobile", None) or None
        if not self.phone: return None, "从北京服务器获取手机号失败"

        bj_room_data_list = app_user.get("memberRoomDataList", []) or []
        room_data_list = []
        for bj_room_data in bj_room_data_list:
            sz_room_data = {
                'role': bj_room_data['role'],
                'role_name': bj_room_data['roleName'],
                'outer_room_id': bj_room_data['roomId'],
                'property_name': '',
                'province': '',
                'city': '',
                'project': '',
                'group': '',
                'build': '',
                'unit': '',
                'room': '',
                'outer_property_id': '',
                'outer_project_id': '',
                'outer_group_id': '',
                'outer_build_id': '',
                'project_group_build_unit_id': 0,
                'password_num': 1000,
            }
            apartment_obj = Basedata_Apartment.objects(outer_room_id=bj_room_data['roomId']).first()
            if apartment_obj:
                sz_room_data.update({
                    'property_name': apartment_obj.property_name,
                    'province': apartment_obj.province,
                    'city': apartment_obj.city,
                    'project': apartment_obj.project,
                    'group': apartment_obj.group,
                    'build': apartment_obj.build,
                    'unit': apartment_obj.unit,
                    'room': apartment_obj.room,
                    'outer_property_id': apartment_obj.outer_property_id,
                    'outer_project_id': apartment_obj.outer_project_id,
                    'outer_group_id': apartment_obj.outer_group_id,
                    'outer_build_id': apartment_obj.outer_build_id,
                    'project_group_build_unit_id': apartment_obj.unit_id,
                    'unit_id': apartment_obj.unit_id,
                    'password_num': apartment_obj.password_num,
                })
            if sz_room_data not in room_data_list: room_data_list.append(sz_room_data)
        self.room_data_list = room_data_list

        return self, ""

    def add_app_user(self):
        db_app_user_list = Basedata_BJ_App_User.objects(outer_app_user_id=self.outer_app_user_id)
        if not db_app_user_list: return self.save(), ""
        db_app_user = db_app_user_list.first()
        db_app_user.app_user_id = self.app_user_id
        db_app_user.phone = self.phone
        db_app_user.room_data_list = self.room_data_list
        db_app_user.updated_time = datetime.datetime.now()
        db_app_user.status = "1"
        return db_app_user.save(), ""

    @classmethod
    def get_app_user_dict_from_bj(cls, value, method=CONST['bj_api_url']['api_method']['get_app_user_by_user_id']):
        url = method % value
        app_user = request_bj_server(method_url=url, data_key="userData", post_flag=False)
        if not app_user or not isinstance(app_user, dict):
            return None, "从北京服务器获取用户信息失败"
        return app_user, ""

    def get_app_user_from_bj(self, value, method=CONST['bj_api_url']['api_method']['get_app_user_by_user_id']):
        app_user, ret = self.get_app_user_dict_from_bj(value, method)
        if not app_user: return app_user, ret
        return self.flush_app_user_info(app_user)

    def set_app_user_from_bj(self, value, method=CONST['bj_api_url']['api_method']['get_app_user_by_user_id']):
        self, ret_str = self.get_app_user_from_bj(value, method)
        if not self: return False, ret_str
        return self.add_app_user()

    def get_app_user_by_phone(self, time=0):
        app_user_list = Basedata_BJ_App_User.objects(phone=self.phone)
        if not app_user_list or (time and app_user_list.first().updated_time.timestamp() < time):
            method = CONST['bj_api_url']['api_method']['get_app_user_by_mobile']
            return self.set_app_user_from_bj(self.phone, method)
        return app_user_list, ""

    def get_app_user_by_outer_app_user_id(self, time=0):
        user = Basedata_BJ_App_User.objects(outer_app_user_id=self.outer_app_user_id).first()
        if not user or (time and user.updated_time.timestamp() < time):
            return self.set_app_user_from_bj(self.outer_app_user_id)
        return user, ""

    @classmethod
    def get_user_by_filter(cls, pos_dict={}, regex_dict={}, page_no=1, page_size=0):
        raw_query = {"status": "1"}
        for k, v in pos_dict.items():
            if v: raw_query.update({"room_data_list.%s" % k: v})
        for k, v in regex_dict.items():
            if v: raw_query.update({k: {"$regex": v}})
        if int(page_size):
            return Basedata_BJ_App_User.objects(__raw__=raw_query).skip((page_no - 1) * page_size).limit(page_size)
        return Basedata_BJ_App_User.objects(__raw__=raw_query)

    def get_app_user_info(self):
        return {
            "id": self.id,
            "app_user_id": self.app_user_id,
            "outer_app_user_id": self.outer_app_user_id,
            "phone": self.phone,
            "room_data_list": self.room_data_list,
            "_bind_door_list": self._bind_door_list,
            "_door_list": self.get_can_open_brake_by_room(),
        }

    def clear_door_list(self):
        self.room_data_list = []
        self.bind_door_list = []
        self._bind_door_list = []
        self.status = "2"
        return self.save()

    def get_can_open_brake_by_room(self):
        try:
            brake_list = []
            for room_data in self.room_data_list:
                brake_list += Brake_Machine.get_user_can_pass_brake_by_room(room_data)
            return brake_list
        except KeyError:
            self.set_app_user_from_bj(self.outer_app_user_id)

    def get_can_open_brake(self):
        brake_list = self._bind_door_list
        return brake_list + self.get_can_open_brake_by_room()

    @classmethod
    @method_set_rds(2)
    def get_can_open_brake_by_outer_app_user_id(cls, oaud):
        app_user, ret_str = Basedata_BJ_App_User(outer_app_user_id=oaud).get_app_user_by_outer_app_user_id(1498724908)
        if not app_user: return [], ret_str
        return app_user.get_can_open_brake(), app_user.room_data_list

    @classmethod
    @method_set_rds(10)
    def get_version_info_list(cls, outer_app_user_id):
        version_list = Brake_Version.objects(status="1", lowest_version__nin=[None,""]).order_by("-version")
        if not version_list: return None, "没有任何版本信息"

        latest_version = version_list.first()

        door_list, room_info = cls.get_can_open_brake_by_outer_app_user_id(oaud=str(outer_app_user_id))
        if not door_list: return None, "开门列表为空"

        project_list = []
        for door in door_list:
            p = door['position']
            project = "%s%s%s" % (p['province'], p['city'], p['project_list'][0]['project'])
            project_list.append((project, p['project_list'][0]['outer_project_id']))
        project_list = list(set(project_list))

        version_info_list = []
        for project, outer_project_id in project_list:
            target_version = Brake_Version.objects(
                __raw__={"project_list.outer_project_id": outer_project_id, "status": "1"}).order_by("-version").first()
            if not target_version: target_version = latest_version
            lowest_version = getattr(target_version, "lowest_version", "") or ""
            version_info = {
                "lowest_version_code": int(lowest_version[1:].replace(".", "")) if lowest_version else 0,
                "version": target_version.version,
                "version_code": int(target_version.version[1:].replace(".", "")),
                "md5sum": target_version.md5sum,
                "file_uri": target_version.file_uri,
            }
            version_info_list.append(
                {
                    "project": project,
                    "outer_project_id": outer_project_id,
                    "version_info": version_info,
                }
            )
        return version_info_list, ""
