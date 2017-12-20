# --*-- coding:utf8 --*--
import datetime
import logging
import time
from bson.objectid import ObjectId
from mongoengine.document import DynamicDocument
from mongoengine.fields import IntField, ListField, DateTimeField, DictField, StringField
from apps.basedata.classes.Basedata_Project import Basedata_Project
from apps.basedata.classes.Basedata_Group import Basedata_Group
from apps.basedata.classes.Basedata_Build import Basedata_Build
from apps.basedata.classes.Basedata_Unit import Basedata_Unit
from apps.basedata.classes.Basedata_Apartment import Basedata_Apartment
from apps.brake.classes.Brake_Machine import Brake_Machine
from apps.common.classes.Base_Class import Base_Class
from apps.common.utils.qd_encrypt import set_card_write_no
from apps.common.utils.sentry_date import get_datetime_by_timestamp
from apps.common.utils.qd_decorator import method_set_rds, method_clear_rds

logger = logging.getLogger('qding')


def flush_white_or_black_card_redis(brake_card, is_delete_card=0):
    func_name = 'Brake_Card.get_black_or_white_card_obj_list'
    for area_info in brake_card.card_area:
        white_cache_params = {'outer_project_id': area_info['outer_project_id'], 'status': 4}
        black_cache_params = {'outer_project_id': area_info['outer_project_id'], 'status': 2}
        method_clear_rds(func_name, white_cache_params)
        method_clear_rds(func_name, black_cache_params)

    if is_delete_card:
        cache_params = {'enc_card_no': brake_card.enc_card_no, 'rpp': brake_card.recently_pass_position}
        method_clear_rds('Brake_Card.get_card_info_for_brake_pass', cache_params)


class Brake_Card(Base_Class, DynamicDocument):
    card_no = IntField(default=0)
    enc_card_no = IntField(default=0)
    card_type = IntField(choices=(1, 2, 3, 4, 5), default=1)  # 1 - 楼盘卡 2 - 组团卡 3 - 楼栋卡 4 - 单元卡  5 - 房卡
    card_validity = DateTimeField(default=datetime.datetime.max)
    card_owner = DictField(default={
        "phone": "",
        "name": "",
        "gender": "",
        "type": "",  # ""-未知，1-租户，2-业主，3-家人，4-商家，5-物业
        "role": "",  # ""-未知，1-祖辈，2-父辈，3-子辈，4-孙辈，5-亲戚，6-朋友，7-家政，8-其他
        "age": "",  # ""-未知，1-10岁以下，2-11~20岁，3-21~30岁，4-31~40岁，5-41~50岁，6-51~60岁，7-61~70岁，8-71~80岁，9-81岁以上
        "family_structure": "",  # ""-未知，1-单人独居，2-二人世界，3-两世之选，4-三世齐居，5-四世同堂
    })
    card_area = ListField(default=[])
    door_list = ListField(default=[])
    black_door_list = ListField(default=[])
    recently_pass_position = StringField()

    meta = {'collection': 'brake_card'}

    @classmethod
    @method_set_rds(24 * 3600)
    def get_card_info_for_brake_pass(cls, enc_card_no, rpp):
        card_obj = Brake_Card.objects(enc_card_no=enc_card_no).first()
        if not card_obj: return {}
        card_obj.recently_pass_position = rpp
        card_obj.updated_time = datetime.datetime.now()
        card_obj.save()
        return {
            "card_no": card_obj.card_no,
            "card_owner": card_obj.card_owner,
            "card_area": card_obj.card_area,
        }

    def add_card(self, db_card_obj):
        if not db_card_obj:
            return self.save()
        else:
            db_card_obj.card_owner = self.card_owner
            db_card_obj.card_area = self.card_area
            db_card_obj.card_validity = self.card_validity
            db_card_obj.card_type = self.card_type
            db_card_obj.door_list = self.door_list
            db_card_obj.status = "1"
            return db_card_obj.save()

    def delete_card_obj(self):
        self.status = "2"
        self.updated_time = datetime.datetime.now()
        self.save()

        flush_white_or_black_card_redis(self, is_delete_card=1)

    def active_card(self):
        self.status = '4'
        self.updated_time = datetime.datetime.now()
        self.save()

        flush_white_or_black_card_redis(self)

    def set_card_while_open_card(self, card_info, id_info, owner_info):
        self.card_no = int(str(card_info['card_no']))
        self.enc_card_no = int(card_info['enc_card_no'])
        self.card_type = int(card_info['card_type'])
        self.card_validity = get_datetime_by_timestamp(int(card_info['card_validity']), "%Y-%m-%d %H:%M:%S")
        self.card_owner = owner_info

        self.card_area, room_list, ret_str = self.set_card_area_by_id_info(id_info)
        if ret_str: return None, ret_str

        self.door_list = self.set_door_list()
        db_card_obj = Brake_Card.objects(card_no=self.card_no).first()
        card_obj = self.add_card(db_card_obj)

        return card_obj, ret_str

    def check_card_no_unique(self, enc_card_no):
        raw_query = {
            "card_no": {"$ne": self.card_no},
            "enc_card_no": enc_card_no,
        }
        return Brake_Card.objects(__raw__=raw_query).first()

    def set_door_list(self):
        door_list = []

        f_dict = {
            1: (Brake_Machine.get_project_brake, lambda area:  {"outer_project_id": area['outer_project_id']}),
            5: (Brake_Machine.get_user_can_pass_brake_by_room, lambda area: {"room_data": area})
        }

        f, get_p = f_dict[self.card_type]

        for area_dict in self.card_area:
            door_list += f(**get_p(area_dict))

        self.door_list = door_list
        return self.door_list

    def set_card_area_by_id_info(self, id_info):
        ret_dict = {
            1: (self.set_card_area_by_project_id_list, "project_id_list"),
            5: (self.set_card_area_by_room_id_list, "room_id_list"),
        }

        f, p_k = ret_dict[self.card_type]

        return f(id_info[p_k])

    @classmethod
    def set_card_area_by_project_id_list(cls, project_id_list):
        unit_info_list, ret_str = [], ''
        for project_dict in project_id_list:
            unit_dict = {}
            project_id = project_dict['project_id']
            db_project_obj = Basedata_Project.objects(project_id=project_id).first()
            unit_dict.update({
                "province": db_project_obj.province,
                "city": db_project_obj.city,
                "project": db_project_obj.project,
                "project_id": project_id,
                "outer_project_id": db_project_obj.outer_project_id,
            })
            if unit_dict not in unit_info_list:
                unit_info_list.append(unit_dict)
        return unit_info_list, [], ret_str

    @classmethod
    def set_card_area_by_room_id_list(cls, room_id_list):
        unit_info_list, room_list, ret_str = [], [], ''
        for room_id in room_id_list:
            db_apartment = Basedata_Apartment.objects(outer_room_id=str(room_id)).first()
            mem = db_apartment.get_apartment_info()
            if mem not in unit_info_list: unit_info_list.append(mem)
            room_list.append(db_apartment)
        return unit_info_list, list(set(room_list)), ret_str

    @classmethod
    def get_card_obj_by_card_no(cls, card_no):
        card_obj_list = Brake_Card.objects(card_no=card_no)
        if not card_obj_list:
            return None, '卡号%s不存在' % card_no
        if card_obj_list.count() > 1:
            return False, '卡号%s不唯一，请联系管理员' % card_no
        return card_obj_list.first(), ''

    @classmethod
    def get_card_obj_by_enc_card_no(cls, enc_card_no):
        card_obj_list = Brake_Card.objects(enc_card_no=enc_card_no)
        if not card_obj_list:
            return None, '卡号%s不存在' % enc_card_no
        if card_obj_list.count() > 1:
            return False, '卡号%s不唯一，请联系管理员' % enc_card_no
        return card_obj_list.first(), ''

    @classmethod
    def get_card_obj_by_id(cls, card_id):
        return Brake_Card.objects(id=card_id).first()

    @classmethod
    def check_status(cls, brake_machine, black_card_no_list, white_card_no_list):
        def _set_card(_enc_card_no, method):
            db_card_obj = Brake_Card.objects(enc_card_no=_enc_card_no).first()
            if not db_card_obj: return
            mac_list = [brake['mac'] for brake in db_card_obj.black_door_list]
            method(db_card_obj, mac_list, brake_machine)
            db_card_obj.save()

        def _remove(db_card_obj, _mac_list, _brake_machine):
            if db_card_obj.status != "4": return
            if _brake_machine['mac'] in _mac_list: db_card_obj.black_door_list.remove(_brake_machine)
            if not db_card_obj.black_door_list: db_card_obj.status = "1"

        def _append(db_card_obj, _mac_list, _brake_machine):
            if db_card_obj.status != "2": return
            if _brake_machine not in _mac_list: db_card_obj.black_door_list.append(_brake_machine)
            if db_card_obj.black_door_list == db_card_obj.door_list: db_card_obj.status = "3"

        for enc_card_no in black_card_no_list: _set_card(enc_card_no, _append)
        for enc_card_no in white_card_no_list: _set_card(enc_card_no, _remove)

    @classmethod
    @method_set_rds(24*3600)
    def get_black_or_white_card_obj_list(cls, outer_project_id, status="2"):
        def _get_ret(_card_obj):
            return {
                "enc_card_no": _card_obj.enc_card_no,
                "updated_time": int(_card_obj.updated_time.timestamp()),
            }
        raw_query = {"status": status, "card_area.outer_project_id": outer_project_id}
        return [_get_ret(card_obj) for card_obj in Brake_Card.objects(__raw__=raw_query)]

    def get_card_obj_info(self):
        card_type_dict = {"1": "物业卡", "5": "业主卡"}
        card_owner_dict = {
            "gender": {"M": "男", "F": "女"},
            "type": {"1": "租户", "2": "业主", "3": "家人", "4": "商家", "5": "物业"},
            "age": {"1": "10岁以下", "2": "11~20岁", "3": "21~30岁", "4": "31~40岁",
                    "5": "41~50岁", "6": "51~60岁", "7": "61~70岁", "8": "71~80岁", "9": "81岁以上"},
            "role": {"1": "祖辈", "2": "父辈", "3": "子辈", "4": "孙辈", "5": "亲戚", "6": "朋友", "7": "家政", "8": "其他"},
            "family_structure": {"1": "单人独居", "2": "二人世界", "3": "两世之选", "4": "三世齐居", "5": "四世同堂"}
        }
        card_owner = self.card_owner
        card_owner.update({
            "gender_str": card_owner_dict['gender'].get(str(self.card_owner.get("gender", "")), "性别"),
            "type_str": card_owner_dict['type'].get(str(self.card_owner.get("type", "")), "用户类型"),
            "age_str": card_owner_dict['age'].get(str(self.card_owner.get("age", "")), "年龄"),
            "role_str": card_owner_dict['role'].get(str(self.card_owner.get("role", "")), "角色"),
            "family_structure_str": card_owner_dict['family_structure'].get(self.card_owner.get("family_structure", ""),
                                                                            "家庭结构"),
        })
        return {
            "status": self.status,
            "id": str(self.id),
            "card_no": self.card_no,
            "card_type": self.card_type,
            "card_type_str": card_type_dict.get(str(self.card_type), "卡类型"),
            "card_validity": int(self.card_validity.timestamp()),
            "card_area": self.card_area,
            "card_owner": card_owner,
            "door_list": [],
            "updated_time": self.updated_time,
            "recently_pass_position": self.recently_pass_position,
            "can_open_door_list": [brake_machine['position_str'] for brake_machine in self.door_list
                                   if brake_machine['mac'] not in [black_machine['mac'] for black_machine
                                                                   in self.black_door_list]]
        }

    @classmethod
    def get_card_by_filter(cls, card_id=None, card_type=None, status=None, province=None, city=None,
                           project=None, group=None, build=None, unit=None, room=None, card_no=None,
                           phone=None, name=None, page_no=1, page_size=30):
        raw_query = {}
        location = {
            "province": province,
            "city": city,
            "project": project,
            "group": group,
            "build": build,
            "unit": unit,
            "room": room,
        }
        owner = {
            "name": name,
            "phone": phone,
        }
        field_dict = {
            "card_type": int(card_type) if card_type else card_type,
            "status": status,
            "_id": ObjectId(card_id) if card_id else None,
        }
        for k, v in location.items():
            if v: raw_query.update({"card_area.%s" % k: v})
        for k, v in owner.items():
            if v: raw_query.update({"card_owner.%s" % k: {"$regex": v}})
        for k, v in field_dict.items():
            if v: raw_query.update({k: v})
        if card_no:
            raw_query.update({"card_no": int(card_no)})
        if int(page_size):
            return Brake_Card.objects(__raw__=raw_query).skip((int(page_no) - 1) * int(page_size)).limit(int(page_size))
        else:
            return Brake_Card.objects(__raw__=raw_query)

    @classmethod
    def get_write_no(cls, card_info, id_info):
        tmp_list = [int(card_info['card_validity'])]
        card_info['card_type'] = int(card_info['card_type'])
        brake_version_list = []

        def _add_brake_version(_base_data_obj):
            brake_machine_list = Brake_Machine.get_project_brake(outer_project_id=_base_data_obj.outer_project_id)
            return [brake_machine['version'] for brake_machine in brake_machine_list]

        if card_info['card_type'] == 5:
            for outer_room_id in id_info['room_id_list']:
                db_apartment_obj = Basedata_Apartment.objects(outer_room_id=str(outer_room_id)).first()
                if not db_apartment_obj: continue
                tmp_list.append(int(db_apartment_obj.unit_id))
                brake_version_list += _add_brake_version(db_apartment_obj)
        else:
            area_level_dict = {
                1: ("project_id", Basedata_Project),
                2: ("group_id", Basedata_Group),
                3: ("build_id", Basedata_Build),
                4: ("unit_id", Basedata_Unit)
            }
            for area_dict in id_info['project_id_list']:
                area_level_id_str, base_data_class = area_level_dict.get(int(card_info.get('card_type')))
                area_level_id = int(area_dict.get(area_level_id_str))
                base_data_obj = base_data_class.objects(**{area_level_id_str: area_level_id}).first()
                if not base_data_obj: continue
                tmp_list.append(area_level_id)
                brake_version_list += _add_brake_version(base_data_obj)

        brake_version_list = list(set(brake_version_list))
        if not brake_version_list:
            return set_card_write_no(tmp_list, int(card_info['enc_card_no']), int(card_info['enc_card_no_count']))

        from apps.common.utils import validate
        for brake_version in brake_version_list:
            version_flag, version_str = validate.validate_version(brake_version)
            if not version_flag:
                return set_card_write_no(tmp_list, int(card_info['enc_card_no']), int(card_info['enc_card_no_count']))
            version_code = int(brake_version[1:].replace(".", ""))
            if version_code < 232:
                return set_card_write_no(tmp_list, int(card_info['enc_card_no']), int(card_info['enc_card_no_count']))

        tmp_list.insert(1, int(time.time()))
        return set_card_write_no(tmp_list, int(card_info['enc_card_no']), int(card_info['enc_card_no_count']), 3)

    def modify_card_obj(self, phone, name, status):
        if phone:
            self.card_owner.update({
                "phone": phone,
            })
        if name:
            self.card_owner.update({
                "name": name,
            })
        if status:
            self.status = status
            self.updated_time = datetime.datetime.now()
        self.save()

        flush_white_or_black_card_redis(self, is_delete_card=1)

