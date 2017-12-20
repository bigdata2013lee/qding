# --*-- coding:utf8 --*--
from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument
from mongoengine.fields import StringField, IntField
import logging

logger = logging.getLogger('qding')


class Basedata_Project(Base_Class, DynamicDocument):
    province = StringField(default="")
    city = StringField(default="")
    property_name = StringField(default="")
    project = StringField(default="")
    room_num = IntField(default=0)
    unit_num = IntField(default=0)

    outer_city_id = StringField(default="")
    outer_property_id = StringField(default="")
    outer_project_id = StringField(default="")

    project_id = IntField(default=0)

    meta = {'collection': 'basedata_project'}

    def get_project_info(self):
        return {
            "province": self.province,
            "city": self.city,
            "project": self.project,
            "property_name": self.property_name,
            "outer_city_id": self.outer_city_id,
            "outer_project_id": self.outer_project_id,
            "outer_property_id": self.outer_property_id,
            "project_id": self.project_id,
        }

    def get_project_id(self):
        if not self.project_id:
            self.set_qd_id()
            self.save()
        return self.project_id

    def set_qd_id(self):
        from apps.common.utils.qd_encrypt import set_basedata_id
        outer_project_id = getattr(self, "outer_project_id", "") or ""
        self.project_id, count = set_basedata_id(outer_project_id, self.check_project_id_exits)
        return self.project_id, ''

    def check_project_id_exits(self, project_id):
        raw_query = {
            "outer_project_id": {"$ne": self.outer_project_id},
            "project_id": project_id,
        }
        return Basedata_Project.objects(__raw__=raw_query)

    def get_project_by_project(self):
        project_obj_list = Basedata_Project.objects(province=self.province, city=self.city, project=self.project)
        if not project_obj_list:
            return None
        return project_obj_list.first()

    def get_project_by_outer_project_id(self):
        project_obj_list = Basedata_Project.objects(outer_project_id=self.outer_project_id)
        if not project_obj_list:
            return None, '%s not exists' % self.outer_project_id
        return project_obj_list.first(), ''

    @classmethod
    def get_project_list_by_filter(cls, page_no=1, page_size=0, **args):
        raw_query = {"status": "1"}
        for k, v in args.items():
            if v: raw_query.update({k: v})
        if int(page_size):
            return Basedata_Project.objects(__raw__=raw_query).skip((int(page_no) - 1) * int(page_size)).limit(
                int(page_size))
        return Basedata_Project.objects(__raw__=raw_query)

    def save_qd_obj(self):
        db_obj = Basedata_Project.objects(outer_project_id=self.outer_project_id).first()
        if not db_obj: return self.save()
        attr_list = ['province', 'city', 'property_name', 'project', 'outer_city_id', 'outer_property_id', 'project_id']
        for attr in attr_list:
            setattr(db_obj, attr, getattr(self, attr, "") or "")
        return db_obj.save()
