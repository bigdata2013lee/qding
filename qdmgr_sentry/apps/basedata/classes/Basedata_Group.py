# --*-- coding:utf8 --*--
from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument
from mongoengine.fields import StringField, IntField
import logging

logger = logging.debug('qding')


class Basedata_Group(Base_Class, DynamicDocument):
    province = StringField(default="")
    city = StringField(default="")
    property_name = StringField(default="")
    project = StringField(default="")
    group = StringField(default="")

    outer_city_id = StringField(default="")
    outer_property_id = StringField(default="")
    outer_project_id = StringField(default="")
    outer_group_id = StringField(default="")

    project_id = IntField(default=0)
    group_id = IntField(default=0)

    meta = {'collection': 'basedata_group'}

    def set_qd_id(self):
        from apps.common.utils.qd_encrypt import set_basedata_id
        outer_project_id = getattr(self, "outer_project_id", "") or ""
        outer_group_id = getattr(self, "outer_group_id", "") or ""
        input_msg = "%s%s" % (outer_project_id, outer_group_id)
        self.group_id, count = set_basedata_id(input_msg, self.check_group_id_exits)
        return self.group_id

    def get_group_id(self):
        if not self.project_id:
            self.set_qd_id()
            self.save()
        return self.group_id

    def check_group_id_exits(self, group_id):
        raw_query = {
            "$or": [{"outer_project_id": {"$ne": self.outer_project_id}},
                    {"outer_group_id": {"$ne": self.outer_group_id}}],
            "group_id": group_id,
        }
        return Basedata_Group.objects(__raw__=raw_query)

    def get_project_group_list(self):
        return Basedata_Group.objects(province=self.province, city=self.city, project=self.project).distinct("group")

    def get_group_by_outer_group_id(self):
        group_obj_list = Basedata_Group.objects(outer_project_id=self.outer_project_id,
                                                outer_group_id=self.outer_group_id)
        if not group_obj_list:
            return None
        if group_obj_list.count() > 1:
            group_obj_list.first().delete()
        return group_obj_list.first()

    def get_group_obj_by_group_id(self):
        group_obj_list = Basedata_Group.objects(project_id=self.project_id, group_id=self.group_id)
        if not group_obj_list:
            return None, "group id %s not exists" % self.group_id
        group_count = group_obj_list.count()
        if group_count > 1:
            group_obj_list.first().delete()
        return group_obj_list.first(), ""

    def get_group_by_group(self):
        return Basedata_Group.objects(province=self.province, city=self.city, project=self.project,
                                      group=self.group).first()

    def get_group_list_by_filter(self, page_no=1, page_size=0):
        raw_query = {"status": "1"}
        if self.province:
            raw_query.update({"province": self.province})
        if self.city:
            raw_query.update({"city": self.city})
        if self.project:
            raw_query.update({"project": self.project})
        if self.group:
            raw_query.update({"group": self.group})
        if self.project_id:
            raw_query.update({"project_id": int(self.project_id)})
        if int(page_size):
            return Basedata_Group.objects(__raw__=raw_query).order_by("province").skip(
                (int(page_no) - 1) * int(page_size)).limit(int(page_size))
        return Basedata_Group.objects(__raw__=raw_query).order_by("province")

    def get_group_info(self):
        return {
            "province": self.province,
            "city": self.city,
            "project": self.project,
            "group": self.group,
            "group_id": self.group_id,
        }

    def get_group_list_by_project(self):
        raw_query = {
            "province": self.province,
            "city": self.city,
            "project": self.project,
        }
        return Basedata_Group.objects(__raw__=raw_query).distinct('group')

    def save_qd_obj(self):
        db_obj = Basedata_Group.objects(outer_project_id=self.outer_project_id, outer_group_id=self.outer_group_id).first()
        if not db_obj: return self.save()
        attr_list = ['province', 'city', 'property_name', 'project', 'group', 'outer_city_id',
                     'outer_property_id', 'group_id']
        for attr in attr_list:
            setattr(db_obj, attr, getattr(self, attr, "") or "")
        return db_obj.save()
