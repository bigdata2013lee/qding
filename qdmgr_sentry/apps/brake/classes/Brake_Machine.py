# -*- coding:utf-8 -*-
import re
import time
import json
import hashlib
from apps.common.utils.redis_client import rc
from mongoengine.document import DynamicDocument
from apps.common.classes.Base_Class import Base_Class
from apps.common.utils.sentry_date import get_datatime
from apps.common.utils.qd_decorator import method_set_rds, json_default
from mongoengine.fields import StringField, IntField, DictField, FloatField, DateTimeField


def flush_redis(position):
    for project_dict in position['project_list']:
        arg1 = {"outer_project_id": project_dict['outer_project_id']}
        arg2 = {"province": position['province'], "city": position['city'], "project": project_dict['project']}
        s1 = json.dumps(arg1, sort_keys=True, default=json_default)
        s2 = json.dumps(arg2, sort_keys=True, default=json_default)
        k1 = hashlib.md5(s1.encode("utf8")).hexdigest()
        k2 = hashlib.md5(s2.encode("utf8")).hexdigest()
        for k in rc.cnn.keys("api_cache:Brake_Machine.get_project_brake*%s" % k1): rc.cnn.delete(k)
        for k in rc.cnn.keys("api_cache:Brake_Machine.get_project_brake*%s" % k2): rc.cnn.delete(k)


class Brake_Machine(DynamicDocument, Base_Class):
    position = DictField(default={
        "province": "",
        "city": "",
        "level": 2,
        "project_list": [
            {
                "project": "",
                "outer_project_id": "",
                "group_list": [],
            }
        ]
    })
    position_str = StringField(default="")
    gate_info = DictField(default={
        "gate_name": "",
        "direction": "I",
    })
    mac = StringField(default="")
    open_time = StringField(default="5")
    bluetooth_rssi = StringField(default="-73")
    wifi_rssi = StringField(default="-73")
    firmware_version = StringField(default="")
    hardware_version = StringField(default="")
    heart_time = FloatField(default=24)
    is_monit = IntField(default=0)
    configure_time = DateTimeField(default=None)
    configure_user = StringField(default="")
    modify_status = IntField(default=0)

    meta = {'collection': 'brake_machine'}

    def add_brake(self):
        brake_machine = Brake_Machine.objects(mac=self.mac, status="1").first()
        flush_redis(self.position)
        if brake_machine:
            brake_machine.position = self.position
            brake_machine.gate_info = self.gate_info
            brake_machine.wifi_rssi = self.wifi_rssi
            brake_machine.bluetooth_rssi = self.bluetooth_rssi
            brake_machine.open_time = self.open_time
            return brake_machine.save()
        return self.save()

    def add_brake_by_configer(self):
        brake_machine = Brake_Machine.objects(mac=self.mac, status="1").first()
        attr_list = ['mac', 'position', 'position_str', 'gate_info', 'bluetooth_rssi', 'wifi_rssi', 'open_time',
                     'firmware_version', 'hardware_version', 'configure_time', 'configure_user']

        flush_redis(self.position)

        if brake_machine:
            for attr in attr_list: setattr(brake_machine, attr, getattr(self, attr))
            return brake_machine.save()
        else:
            return self.save()

    def modify_brake(self, brake):
        brake.wifi_rssi = self.wifi_rssi
        brake.bluetooth_rssi = self.bluetooth_rssi
        brake.open_time = self.open_time
        brake.position['level'] = int(self.level)
        brake.firmware_version = self.firmware_version

        flush_redis(brake.position)

        return brake.save()

    @classmethod
    @method_set_rds(3600)
    def get_brake_by_mac(cls, mac):
        return Brake_Machine.objects(mac=mac, status="1").first()

    @classmethod
    def get_brake_info_for_pass(cls, brake_obj):
        if not brake_obj: return {}
        return {
            "position": brake_obj.position,
            "position_str": brake_obj.position_str,
            "gate_info": brake_obj.gate_info,
            "mac": brake_obj.mac,
            "id": str(brake_obj.id),
        }

    @classmethod
    def get_user_can_pass_brake_by_room(cls, room_data):
        brake_list = []

        project_brake_list = cls.get_project_brake(outer_project_id=room_data['outer_project_id'])

        group_brake_list = []
        build_brake_list = []
        unit_brake_list = []

        def _compare_pos(brake, room_data, deep):
            if room_data['outer_group_id']:
                for project_dict in brake['position']['project_list']:
                    if project_dict['outer_project_id'] != room_data['outer_project_id']: continue
                    for group_dict in project_dict['group_list']:
                        if group_dict['outer_group_id'] != room_data['outer_group_id']: continue
                        if deep == 0: return True
                        if deep >= 1:
                            for build_dict in group_dict['build_list']:
                                if build_dict['outer_build_id'] != room_data['outer_build_id']: continue
                                if deep == 1: return True
                                for unit_dict in build_dict['unit_dict_list']:
                                    if unit_dict['project_group_build_unit_id'] != room_data['unit_id']: continue
                                    return True
            else:
                if deep == 0: return False
                for project_dict in brake['position']['project_list']:
                    if project_dict['outer_project_id'] != room_data['outer_project_id']: continue
                    for group_dict in project_dict['group_list']:
                        for build_dict in group_dict['build_list']:
                            if build_dict['outer_build_id'] != room_data['outer_build_id']: continue
                            if deep == 1: return True
                            for unit_dict in build_dict['unit_dict_list']:
                                if unit_dict['project_group_build_unit_id'] != room_data['unit_id']: continue
                                return True
            return False

        for brake in project_brake_list:
            if brake['position']['level'] == 5:
                unit_brake_list.append(brake)
            elif brake['position']['level'] == 4:
                build_brake_list.append(brake)
            elif brake['position']['level'] == 3:
                group_brake_list.append(brake)
            elif brake['position']['level'] == 2:
                brake_list.append(brake)

        for com_list, deep in zip([group_brake_list, build_brake_list, unit_brake_list], [0, 1, 2]):
            for brake in com_list:
                if _compare_pos(brake, room_data, deep): brake_list.append(brake)

        return brake_list

    @classmethod
    def get_machine_by_position(cls, province=None, city=None, project=None, group=None, lately_pass=None,
                                build=None, unit=None, mac=None, brake_type=None, page_no=1, page_size=0,
                                order_field="created_time", status="1"):
        raw_query = {}
        if status:
            raw_query.update({"status": status})
        if province:
            raw_query.update({"position.province": province})
        if city:
            raw_query.update({"position.city": city})
        if project:
            raw_query.update({"position.project_list.project": project})
        if group:
            raw_query.update({"position.project_list.group_list.group": group})
        if build:
            raw_query.update({"position.project_list.group_list.build_list.build": build})
        if unit:
            raw_query.update({"position.project_list.group_list.build_list.unit_dict_list.unit": unit})
        if mac:
            raw_query.update({"mac": {"$regex": mac}})
        if brake_type == "1":
            raw_query.update({"position.level": 2})
        if brake_type == "2":
            raw_query.update({"position.level": {"$ne": 2}})
        if lately_pass:
            raw_query.update({"updated_time": {"$lte": get_datatime(-int(lately_pass))}})
        if page_size:
            start = (int(page_no) - 1) * int(page_size)
            end = start + int(page_size)
            return Brake_Machine.objects(__raw__=raw_query).order_by(order_field)[start:end]
        return Brake_Machine.objects(__raw__=raw_query).order_by(order_field)

    @classmethod
    def get_machine_by_filter(cls, page_no=1, page_size=0, order_field="created_time",
                              position={}, reg_dict={}, lately_pass=None, brake_type=None, **kargs):
        raw_query = {}
        for k, v in kargs.items():
            if v: raw_query.update({k: v})
        for k, v in position.items():
            if v: raw_query.update({k: v})
        for k, v in reg_dict.items():
            if v: raw_query.update({k: {"$regex": v}})
        if lately_pass:
            raw_query.update({"updated_time": {"$lte": get_datatime(-int(lately_pass))}})
        if brake_type == "1":
            raw_query.update({"position.level": 2})
        if brake_type == "2":
            raw_query.update({"position.level": {"$ne": 2}})
        if page_size:
            start = (int(page_no) - 1) * int(page_size)
            end = start + int(page_size)
            return Brake_Machine.objects(__raw__=raw_query).order_by(order_field)[start:end]
        return Brake_Machine.objects(__raw__=raw_query).order_by(order_field)

    @classmethod
    def make_position_str(cls, position, gate_info):
        position_str = ""
        level = position["level"]
        for project_dict in position["project_list"]:
            position_str = "%s%s" % (position_str, project_dict["project"])
            if level == 2: continue
            for group_dict in project_dict["group_list"]:
                position_str = "%s%s" % (position_str, group_dict["group"])
                if level == 3: continue
                for build_dict in group_dict["build_list"]:
                    build_name = build_dict["build"]
                    build_re = re.compile('.*栋$')
                    if not build_re.match(build_name): build_name = u"%s栋" % build_name
                    position_str = "%s%s" % (position_str, build_name)
                    if level == 4: continue
                    for unit_dict in build_dict["unit_dict_list"]:
                        unit_re = re.compile('.*单元$')
                        if not unit_re.match(unit_dict['unit']): unit = u"%s单元" % str(unit_dict['unit'])
                        position_str = "%s%s" % (position_str, unit)
        gate_name = gate_info["gate_name"]
        direction = gate_info["direction"]
        position_str = "%s%s入" % (position_str, gate_name)
        if direction == "O": position_str = "%s%s出" % (position_str, gate_name)
        return position_str

    def get_brake_info(self):
        position = getattr(self, "position", {}) or {}
        online_status = self.check_brake_status()
        brake_info = {
            "id": str(self.id),
            "mac": self.mac,
            "position": position,
            "level": position.get("level", 0),
            "province": position.get("province", "") or "",
            "city": position.get("city", "") or "",
            "project": position['project_list'][0]['project'],
            "position_str": self.position_str,
            "direction": self.gate_info.get("direction", "I"),
            "gate_name": self.gate_info.get("gate_name", ""),
            "wifi_rssi": getattr(self, "wifi_rssi", "-73") or "-73",
            "bluetooth_rssi": getattr(self, "bluetooth_rssi", "-73") or "-73",
            "open_time": getattr(self, "open_time", "5") or "5",
            "command": getattr(self, "command", "0") or "0",
            "firmware_version": getattr(self, "firmware_version", "") or "",
            "hardware_version": getattr(self, "hardware_version", "") or "",
            "is_monit": getattr(self, "is_monit", 0) or 0,
            "heart_time": getattr(self, "heart_time", 24) or 24,
            "online_status": online_status,
            "online_status_str": "在线" if online_status else "掉线",
            "updated_time": int(self.updated_time.timestamp()),
            "updated_time_str": self.updated_time,
            "status": self.status,
            "configure_time": int(self.configure_time.timestamp()) if self.configure_time else 0,
            "configure_user": self.configure_user,
        }
        return brake_info

    def check_brake_status(self):
        brake_time = int(self.updated_time.timestamp())
        heart_time = getattr(self, "heart_time", 0) or 0
        if int(time.time()) - brake_time > heart_time * 3600:
            return 0
        else:
            return 1

    @classmethod
    def make_position(cls, project_obj, group_obj, build_obj, unit_obj):
        position = {
            "level": 2,
            "province": project_obj.province,
            "city": project_obj.city,
            "project_list": [
                {
                    "project": project_obj.project,
                    "outer_project_id": project_obj.outer_project_id,
                    "group_list": [],
                }
            ]
        }
        group_dict = {}
        if unit_obj:
            position['level'] = 5
            group_dict.update(
                {
                    'group': unit_obj.group,
                    'outer_group_id': unit_obj.outer_group_id,
                    'build_list': [
                        {
                            "outer_build_id": unit_obj.outer_build_id,
                            "build": unit_obj.build,
                            "unit_dict_list": [
                                {
                                    "unit": unit_obj.unit,
                                    "project_group_build_unit_id": unit_obj.unit_id,
                                    "password_num": unit_obj.password_num if unit_obj.password_num else 1500,
                                }
                            ]
                        }
                    ]
                }
            )
        elif build_obj:
            position['level'] = 4
            group_dict.update(
                {
                    'group': build_obj.group,
                    'outer_group_id': build_obj.outer_group_id,
                    'build_list': [
                        {
                            "outer_build_id": build_obj.outer_build_id,
                            "build": build_obj.build
                        }
                    ]
                }
            )
        elif group_obj:
            position['level'] = 3
            group_dict.update({
                "group": group_obj.group,
                "outer_group_id": group_obj.outer_group_id,
                "build_list": []
            })

        if group_dict: position['project_list'][0]['group_list'].append(group_dict)
        return position

    @classmethod
    @method_set_rds(24 * 3600)
    def get_project_brake(cls, province=None, city=None, project=None, outer_project_id=None):
        def __get_brake_info(brake):
            position = getattr(brake, "position", {}) or {}
            online_status = brake.check_brake_status()
            return {
                "id": str(brake.id),
                "mac": brake.mac,
                "level": position.get("level", 0),
                "hardware_version": brake.hardware_version,
                "version": brake.firmware_version,
                "position": position,
                "position_str": brake.position_str,
                "province": position.get("province", "") or "",
                "city": position.get("city", "") or "",
                "project": position['project_list'][0]['project'],
                "gate_info": brake.gate_info,
                "gate_name": brake.gate_info.get("gate_name", ""),
                "direction": brake.gate_info.get("direction", "I"),
                "bluetooth_rssi": brake.bluetooth_rssi,
                "wifi_rssi": brake.wifi_rssi,
                "open_time": brake.open_time,
                "updated_time": int(brake.updated_time.timestamp()),
                "updated_time_str": brake.updated_time,
                "online_status_str": "在线" if online_status else "掉线",
            }

        raw_query = {"status": "1"}
        if outer_project_id:
            raw_query.update({"position.project_list.outer_project_id": outer_project_id})
        else:
            raw_query.update(
                {
                    "position.province": province,
                    "position.city": city,
                    "position.project_list.project": project
                }
            )
        brake_obj_list = Brake_Machine.objects(__raw__=raw_query)
        return [__get_brake_info(brake_obj) for brake_obj in brake_obj_list]
