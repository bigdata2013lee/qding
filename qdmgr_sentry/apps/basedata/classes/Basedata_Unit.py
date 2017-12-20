# --*-- coding:utf8 --*--
from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument

from mongoengine.fields import IntField, StringField
import logging

logger = logging.getLogger('qding')


class Basedata_Unit(Base_Class, DynamicDocument):
    province = StringField(default="")
    city = StringField(default="")
    property_name = StringField(default="")
    project = StringField(default="")
    group = StringField(default="")
    build = StringField(default="")
    unit = StringField(default="")

    outer_city_id = StringField(default="")
    outer_property_id = StringField(default="")
    outer_project_id = StringField(default="")
    outer_group_id = StringField(default="")
    outer_build_id = StringField(default="")

    project_id = IntField(default=0)
    group_id = IntField(default=0)
    build_id = IntField(default=0)
    unit_id = IntField(default=0)

    room_num = IntField(default=0)
    password_num = IntField(default=0)

    meta = {'collection': 'basedata_unit'}

    def set_qd_id(self):
        from apps.common.utils.qd_encrypt import set_basedata_id
        outer_project_id = getattr(self, "outer_project_id", "") or ""
        outer_group_id = getattr(self, "outer_group_id", "") or ""
        outer_build_id = getattr(self, "outer_build_id", "") or ""
        unit = getattr(self, "unit", "") or ""
        input_msg = "%s%s%s%s" % (outer_project_id, outer_group_id, outer_build_id, unit)
        self.unit_id, count = set_basedata_id(input_msg, self.check_unit_id_exits)
        return self.unit_id

    def get_unit_id(self):
        if not self.unit_id:
            self.set_qd_id()
            self.save()
        return self.unit_id

    def check_unit_id_exits(self, unit_id):
        raw_query = {
            "outer_project_id": self.outer_project_id,
            "unit_id": unit_id,
            "$or": [{"unit": {"$ne": self.unit}}, {"outer_build_id": {"$ne": self.outer_build_id}}]
        }
        if self.outer_group_id:
            raw_query["$or"].append({
                "outer_group_id": {"$ne": self.outer_group_id}
            })
        return Basedata_Unit.objects(__raw__=raw_query)

    def get_unit_info(self):
        return {
            "province": self.province,
            "city": self.city,
            "project": self.project,
            "group": self.group,
            "build": self.build,
            "build_str": "%s栋" % self.build,
            "unit": self.unit,
            "unit_str": "%s单元" % self.unit,
            "unit_id": self.unit_id,
        }

    def get_project_dict(self):
        group_name_list = Basedata_Unit.objects(outer_project_id=self.outer_project_id).distinct('group')
        group_list = []
        if not group_name_list:
            group_list = [self.get_group_dict()]
        for group in group_name_list:
            group_list.append(self.get_group_dict(group))
        project_dict = {
            "project": self.project,
            "project_id": self.project_id,
            "outer_project_id": self.outer_project_id,
            "group_list": group_list,
        }
        return project_dict

    def get_group_dict(self, group=""):
        if group:
            self.group = group
            db_unit_obj = Basedata_Unit.objects(outer_project_id=self.outer_project_id, group=group).first()
            build_list = Basedata_Unit.objects(outer_project_id=self.outer_project_id, group=group).distinct("build")
        else:
            db_unit_obj = self
            build_list = Basedata_Unit.objects(outer_project_id=self.outer_project_id).distinct("build")
        group_dict = {
            "group": group,
            "group_id": getattr(db_unit_obj, "group_id", 0) or 0,
            "outer_group_id": getattr(db_unit_obj, "outer_group_id", "") or "",
            "build_list": []
        }
        for build in build_list:
            build_dict = {}
            self.build = build
            if group:
                db_unit_obj = Basedata_Unit.objects(outer_project_id=self.outer_project_id, group=group, build=build).first()
                unit_list = Basedata_Unit.objects(outer_project_id=self.outer_project_id, group=group, build=build).distinct("unit")
            else:
                db_unit_obj = Basedata_Unit.objects(outer_project_id=self.outer_project_id, build=build).first()
                unit_list = Basedata_Unit.objects(outer_project_id=self.outer_project_id, build=build).distinct("unit")
            build_dict.update(
                {
                    "build": build,
                    "build_id": getattr(db_unit_obj, "build_id", 0) or 0,
                    "outer_build_id": getattr(db_unit_obj, "outer_build_id", "") or "",
                    "unit_list": unit_list,
                    "unit_dict_list": self.get_unit_dict_list(),
                }
            )
            group_dict["build_list"].append(build_dict)
        return group_dict

    def get_unit_dict_list(self):
        unit_dict_list = []
        if self.group:
            unit_obj_list = Basedata_Unit.objects(outer_project_id=self.outer_project_id, group=self.group, build=self.build)
        else:
            unit_obj_list = Basedata_Unit.objects(outer_project_id=self.outer_project_id, build=self.build)
        for unit_obj in unit_obj_list:
            unit_dict = {
                "unit": unit_obj.unit,
                "project_group_build_unit_id": unit_obj.unit_id,
                "password_num": unit_obj.password_num if unit_obj.password_num else 1500,
            }
            if unit_dict not in unit_dict_list:
                unit_dict_list.append(unit_dict)
        return unit_dict_list

    def get_password_num(self, project_room_num):
        if not self.password_num:
            self.password_num = self.set_password_num(project_room_num)
            self.save()
        return self.password_num

    def set_password_num(self, project_room_num):
        if not project_room_num: project_room_num = 1500
        if not self.room_num: self.room_num = 100
        self.password_num = int(15000 / project_room_num * self.room_num)
        return self.password_num

    def get_unit_list_by_build(self):
        raw_query = {
            "province": self.province,
            "city": self.city,
            "project": self.project,
            "build": self.build,
        }
        if self.group:
            raw_query.update({
                "group": self.group
            })
        return Basedata_Unit.objects(__raw__=raw_query).distinct('unit')

    def get_unit_obj_by_unit_id(self):
        unit_obj_list = Basedata_Unit.objects(project_id=self.project_id, unit_id=self.unit_id)
        if not unit_obj_list:
            return None, "unit id %s not exists" % self.unit_id
        unit_count = unit_obj_list.count()
        if unit_count > 1:
            return False, 'the count of unit id %s is not unique,it has %s' % (self.unit_id, unit_count)
        return unit_obj_list.first(), ""

    def get_unit_list_by_filter(self, page_no=1, page_size=0):
        raw_query = {"status": "1"}
        if self.province:
            raw_query.update({"province": self.province})
        if self.city:
            raw_query.update({"city": self.city})
        if self.project:
            raw_query.update({"project": self.project})
        if self.group:
            raw_query.update({"group": self.group})
        if self.build:
            raw_query.update({"build": self.build})
        if self.unit:
            raw_query.update({"build": self.unit})
        if self.project_id:
            raw_query.update({"project_id": int(self.project_id)})
        if self.group_id:
            raw_query.update({"group_id": int(self.group_id)})
        if self.build_id:
            raw_query.update({"build_id": int(self.build_id)})
        if int(page_size):
            return Basedata_Unit.objects(__raw__=raw_query).order_by("province").skip(
                (int(page_no) - 1) * int(page_size)).limit(int(page_size))
        return Basedata_Unit.objects(__raw__=raw_query).order_by("province")

    def save_qd_obj(self):
        db_obj = Basedata_Unit.objects(outer_project_id=self.outer_project_id,
                                       outer_group_id=self.outer_group_id,
                                       outer_build_id=self.outer_build_id,
                                       unit=self.unit).first()
        if not db_obj: return self.save()
        attr_list = ['province', 'city', 'property_name', 'project', 'group', 'build', 'outer_city_id',
                     'outer_property_id', 'unit_id']
        for attr in attr_list:
            setattr(db_obj, attr, getattr(self, attr, "") or "")
        return db_obj.save()
