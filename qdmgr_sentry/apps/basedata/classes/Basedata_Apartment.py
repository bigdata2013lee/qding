# -*- coding:utf-8 -*-
from mongoengine.fields import StringField, IntField
from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument

from settings.const import CONST
from apps.common.utils.request_api import request_bj_server

from apps.common.utils.redis_client import rc


class Basedata_Apartment(DynamicDocument, Base_Class):
    province = StringField(default="")
    city = StringField(default="")
    property_name = StringField(default="")
    project = StringField(default="")
    group = StringField(default="")
    build = StringField(default="")
    unit = StringField(default="")
    room = StringField(default="")

    outer_city_id = StringField(default="")
    outer_property_id = StringField(default="")
    outer_project_id = StringField(default="")
    outer_group_id = StringField(default="")
    outer_build_id = StringField(default="")
    outer_room_id = StringField(default="")

    project_id = IntField(default=0)
    group_id = IntField(default=0)
    build_id = IntField(default=0)
    unit_id = IntField(default=0)

    password_num = IntField(default=0)

    meta = {'collection': 'basedata_apartment'}

    def get_apartment_by_project_id(self):
        return Basedata_Apartment.objects(outer_project_id=self.outer_project_id)

    def get_apartment_by_filter(self, page_size=0, page_no=1):
        raw_query = {"status": "1"}
        filter_list = ['province', 'city', 'project', 'outer_project_id', 'project_id',
                       'group', 'outer_group_id', 'group_id', 'build', 'outer_build_id',
                       'build_id', 'unit', 'unit_id']
        regex_filter_list = ['room', 'outer_room_id']
        for fil in filter_list:
            if getattr(self, fil): raw_query.update({fil: getattr(self, fil)})
        for re_fil in regex_filter_list:
            if getattr(self, re_fil): raw_query.update({re_fil: {"$regex": getattr(self, re_fil)}})
        if int(page_size):
            skip = (int(page_no) - 1) * int(page_size)
            return Basedata_Apartment.objects(__raw__=raw_query).skip(skip).limit(int(page_size))
        else:
            return Basedata_Apartment.objects(__raw__=raw_query)

    def get_apartment_from_bj(self):
        method_url = CONST['bj_api_url']['api_method']['get_room_data_by_room_id'] % self.outer_room_id
        response = request_bj_server(method_url=method_url)
        if not response: return None
        self.province = response.get("province", "").replace("省", "")
        self.city = response.get("cityName", "").replace("市", "")
        self.project = response.get("projectName", "")
        self.group = response.get("groupName", "")
        self.build = response.get("buildingName", "").replace("栋", "").replace("单元", "")
        self.unit = response.get("unit", "").replace("单元", "").replace("栋", "")
        self.room = response.get("roomName", "").replace("栋", "").replace("单元", "")
        self.outer_city_id = str(response.get("cityId", ""))
        self.outer_project_id = str(response.get("projectId", ""))
        self.outer_group_id = str(response.get("groupId", ""))
        self.outer_build_id = str(response.get("buildingId", ""))
        if not self.province or not self.city or not self.project \
                or not self.build or not self.unit or not self.room \
                or not self.outer_project_id or not self.outer_build_id:
            return False
        rc.sadd("sync_project_data", self.outer_project_id)
        return self.save()

    def get_apartment_info(self):
        return {
            "province": self.province,
            "city": self.city,
            "property_name": self.property_name,
            "project": self.project,
            "group": self.group,
            "build": self.build,
            "unit": self.unit,
            "room": self.room,
            "outer_property_id": self.outer_property_id,
            "outer_project_id": self.outer_project_id,
            "outer_group_id": self.outer_group_id,
            "outer_build_id": self.outer_build_id,
            "outer_room_id": self.outer_room_id,
            "project_id": self.project_id,
            "group_id": self.group_id,
            "build_id": self.build_id,
            "unit_id": self.unit_id,
        }

    def get_apartment_by_room_id(self):
        apartment_obj_list = Basedata_Apartment.objects(outer_room_id=self.outer_room_id)
        if not apartment_obj_list:
            apartment_obj = None
            if self.outer_room_id: apartment_obj = self.get_apartment_from_bj()
            return apartment_obj, "房间号%s不存在" % self.outer_room_id
        return apartment_obj_list.first(), ""

    def get_apartment_list_unit(self):
        return Basedata_Apartment.objects(province=self.province, city=self.city, project=self.project,
                                          build=self.build, unit=self.unit)

    def get_room_info(self):
        province = getattr(self, "province", "") or ""
        city = getattr(self, "city", "") or ""
        project = getattr(self, "project", "") or ""
        group = getattr(self, "group", "") or ""
        build = getattr(self, "build", "") or ""
        if "栋" not in build:
            build = "%s栋" % build
        unit = getattr(self, "unit", "") or ""
        if "单元" not in unit:
            unit = "%s单元" % unit
        room = getattr(self, "room", "") or ""
        city_str = "%s%s" % (province, city) if province != city else city
        return "%s%s%s%s%s%s" % (city_str, project, group, build, unit, room)

    def get_project_room_num(self):
        project_room_num = Basedata_Apartment.objects(outer_project_id=self.outer_project_id).count()
        if not project_room_num: project_room_num = 1500
        return project_room_num

    def get_unit_room_num(self):
        raw_query = {
            "outer_project_id": self.outer_project_id,
            "outer_build_id": self.outer_build_id,
            "unit": self.unit
        }
        if self.outer_group_id:
            raw_query.update({
                "outer_group_id": self.outer_group_id
            })
        unit_room_num = Basedata_Apartment.objects(__raw__=raw_query).count()
        if not unit_room_num: unit_room_num = 100
        return unit_room_num

    def get_room_list(self):
        raw_query = {
            "province": self.province,
            "city": self.city,
            "project": self.project,
            "build": self.build,
            "unit": self.unit,
        }
        if self.group:
            raw_query.update({
                "group": self.group
            })
        apartment_list = Basedata_Apartment.objects(__raw__=raw_query)
        return [apartment.room for apartment in apartment_list]

    def save_qd_obj(self):
        db_obj = Basedata_Apartment.objects(outer_project_id=self.outer_project_id,
                                            outer_group_id=self.outer_group_id,
                                            outer_build_id=self.outer_build_id,
                                            unit=self.unit, outer_room_id=self.outer_room_id).first()
        if not db_obj: return self.save()
        attr_list = ['province', 'city', 'property_name', 'project', 'group', 'build', 'room', 'outer_city_id',
                     'outer_property_id']
        for attr in attr_list:
            setattr(db_obj, attr, getattr(self, attr, "") or "")
        return db_obj.save()

    def set_qd_id(self):
        pass
