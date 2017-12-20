# --*-- coding:utf8 --*--
from mongoengine.document import DynamicDocument
from mongoengine.fields import StringField, IntField

from apps.common.classes.Base_Class import Base_Class

import logging

logger = logging.getLogger('qding')


class Basedata_Build(Base_Class, DynamicDocument):
    province = StringField(default="")
    city = StringField(default="")
    property_name = StringField(default="")
    project = StringField(default="")
    group = StringField(default="")
    build = StringField(default="")

    outer_city_id = StringField(default="")
    outer_property_id = StringField(default="")
    outer_project_id = StringField(default="")
    outer_group_id = StringField(default="")
    outer_build_id = StringField(default="")

    project_id = IntField(default=0)
    group_id = IntField(default=0)
    build_id = IntField(default=0)

    meta = {'collection': 'basedata_build'}

    def set_qd_id(self):
        from apps.common.utils.qd_encrypt import set_basedata_id
        outer_project_id = getattr(self, "outer_project_id", "") or ""
        outer_group_id = getattr(self, "outer_group_id", "") or ""
        outer_build_id = getattr(self, "outer_build_id", "") or ""
        input_msg = "%s%s%s" % (outer_project_id, outer_group_id, outer_build_id)
        self.build_id, count = set_basedata_id(input_msg, self.check_build_id_exits)
        return self.build_id

    def get_build_id(self):
        if not self.build_id:
            self.set_qd_id()
            self.save()
        return self.build_id

    def check_build_id_exits(self, build_id):
        raw_query = {
            "$or": [{"outer_project_id": {"$ne": self.outer_project_id}},
                    {"outer_build_id": {"$ne": self.outer_build_id}}],
            "build_id": build_id
        }
        if self.outer_group_id:
            raw_query['$or'].append({"outer_group_id": {"$ne": self.outer_group_id}})
        return Basedata_Build.objects(__raw__=raw_query)

    def get_build_obj_by_outer_build_id(self):
        raw_query = {
            "outer_project_id": self.outer_project_id,
            "outer_build_id": self.outer_build_id,
        }
        if self.outer_group_id:
            raw_query.update({
                "outer_group_id": self.outer_group_id
            })
        return Basedata_Build.objects(__raw__=raw_query).first()

    def get_build_obj_by_build_id(self):
        build_obj_list = Basedata_Build.objects(project_id=self.project_id, build_id=self.build_id)
        if not build_obj_list:
            return None, "build id %s not exists" % self.build_id
        build_count = build_obj_list.count()
        if build_count > 1:
            return False, 'the count of build id %s is not unique,it has %s' % (self.build_id, build_count)
        return build_obj_list.first(), ""

    def get_build_list_by_project_or_group(self):
        raw_query = {
            "province": self.province,
            "city": self.city,
            "project": self.project
        }
        if self.group:
            raw_query.update({
                "group": self.group
            })
        return Basedata_Build.objects(__raw__=raw_query).distinct('build')

    def get_build_list_by_filter(self, page_no=1, page_size=0):
        raw_query = {"status": "1"}
        for attr in ['province', 'city', 'project', 'group', 'build']:
            v = getattr(self, attr, None) or None
            if v: raw_query.update({attr: v})

        for attr in ['project_id', 'group_id']:
            v = getattr(self, attr, None) or None
            if v: raw_query.update({attr: int(v)})

        if int(page_size):
            return Basedata_Build.objects(__raw__=raw_query).order_by("province").skip(
                (int(page_no) - 1) * int(page_size)).limit(int(page_size))
        return Basedata_Build.objects(__raw__=raw_query).order_by("province")

    def get_build_info(self):
        return {
            "province": self.province,
            "city": self.city,
            "project": self.project,
            "group": self.group,
            "build": self.build,
            "build_str": "%s栋" % self.build,
            "group_id": self.group_id,
            "build_id": self.build_id,
        }

    def save_qd_obj(self):
        db_obj = Basedata_Build.objects(outer_project_id=self.outer_project_id,
                                        outer_group_id=self.outer_group_id, outer_build_id=self.outer_build_id).first()
        if not db_obj: return self.save()
        attr_list = ['province', 'city', 'property_name', 'project', 'group', 'build', 'outer_city_id',
                     'outer_property_id', 'build_id']
        for attr in attr_list:
            setattr(db_obj, attr, getattr(self, attr, "") or "")
        return db_obj.save()
