# -*- coding: utf-8 -*-
from mongoengine.document import DynamicDocument
from apps.common.classes.Base_Class import Base_Class
from mongoengine.fields import StringField, ListField

from apps.common.utils.qd_decorator import method_set_rds


class Brake_Version(DynamicDocument, Base_Class):
    version = StringField(default="")
    lowest_version = StringField(default="")
    former_version = StringField(default="")
    file_uri = StringField(default="")
    md5sum = StringField(default="")
    message = StringField(default="")
    project_list = ListField(default=[])  # 可升级的社区列表 {province,city,project,outer_project_id, project_flag}

    meta = {'collection': 'brake_version'}

    def check_upgrade(self, brake_machine, result={'msg': '', 'data': {'flag': 'N'}}):
        brake_version = self.get_me_by_filter(["former_version"]).first()
        if not brake_version:
            result['msg'] = '版本信息不存在'
            return None
        brake_machine = brake_machine.get_me_by_filter(fields_list=['gate'], use_by_basedata=True).first()
        if not brake_machine:
            result['msg'] = '该位置不存在闸机'
            return None
        brake_machine.version = brake_version
        brake_machine.save()
        return brake_version

    def get_newest_version(self):
        brake_version_obj = Brake_Version.objects.order_by("-created_time").first()
        return brake_version_obj.get_version_info() if brake_version_obj else {}

    def get_all_version_list(self):
        return Brake_Version.objects(status="1")

    def get_all_version_list_sorted(self):
        return Brake_Version.objects(status="1").order_by("-created_time")

    def get_version_info(self):
        return {
            "lowest_version": getattr(self, "lowest_version", "") or "",
            "version": self.version,
            "former_version": self.former_version,
            "file_uri": self.file_uri,
            "md5sum": self.md5sum,
            "id": str(self.id),
            "message": getattr(self, "message", "") or "",
            "created_time": self.created_time,
            "project_list": getattr(self, "project_list", []) or [],
        }

    def get_version_info_for_config(self):
        return {
            "version": self.version,
            "former_version": self.former_version,
            "file_uri": self.file_uri,
            "md5sum": self.md5sum,
        }

    def get_version_info_for_upgrade(self):
        return {
            "version": self.version,
            "file_uri": self.file_uri,
            "md5sum": self.md5sum,
        }

    def add_brake_version(self):
        if self.former_version and not Brake_Version.objects(version=self.former_version, status='1'):
            return 1
        if Brake_Version.objects(former_version=self.former_version, version=self.version, status='1'):
            return 2
        return self.save()

    def get_brake_version_by_id(self):
        return Brake_Version.objects(id=self.id).first()

    def remove_brake_version(self):
        brake_version_obj = self.get_brake_version_by_id()
        if brake_version_obj:
            brake_version_obj.status = '2'
            brake_version_obj.save()
            return True
        return False

    def get_version_by_version(self):
        version_obj_list = Brake_Version.objects(version=self.version, status='1')
        if not version_obj_list:
            return None
        return version_obj_list.first()

    @classmethod
    @method_set_rds()
    def get_version_list_for_config(cls, province=None, city=None, project=None, outer_project_id=None):
        def __get_version_info(version_obj):
            return {
                "version": version_obj.version,
                "former_version": version_obj.former_version,
                "file_uri": version_obj.file_uri,
                "md5sum": version_obj.md5sum,
            }
        all_brake_version_list = list(Brake_Version.objects(status="1"))
        raw_query = {
            "$and": [{"project_list": {"$ne": None}}, {"project_list": {"$ne": []}}],
            "status": "1",
        }
        if outer_project_id:
            raw_query.update({"project_list.outer_project_id": {"$ne":outer_project_id}})
        else:
            project_flag = "%s%s%s" % (province, city, project)
            raw_query.update({"project_list.project_flag": {"$ne": project_flag}})
        filter_brake_version_list = Brake_Version.objects(__raw__=raw_query)
        for brake_version in filter_brake_version_list:
            all_brake_version_list.remove(brake_version)
        return [__get_version_info(brake_version) for brake_version in all_brake_version_list]
