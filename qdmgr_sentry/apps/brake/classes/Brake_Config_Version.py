# -*- coding:utf8 -*-
from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument
from mongoengine.fields import StringField


class Brake_Config_Version(Base_Class, DynamicDocument):
    version = StringField(default="")
    former_version = StringField(default="")
    file_uri = StringField(default="")
    md5sum = StringField(default="")
    message = StringField(default="")

    meta = {'collection': 'brake_config_version'}

    def check_upgrade(self):
        config_version_list = self.get_version_by_filter()
        return config_version_list.order_by("-version").first()

    def add_version(self):
        config_version_list = self.get_version_by_filter()
        if config_version_list: return None
        return self.save()

    def get_version_by_filter(self):
        raw_query = {}
        if self.status:
            raw_query.update({"status": self.status})
        if self.former_version:
            raw_query.update({"former_version": self.former_version})
        if self.version:
            raw_query.update({"version": self.version})
        return Brake_Config_Version.objects(__raw__=raw_query)

    def get_version_by_id(self):
        return Brake_Config_Version.objects(id=self.id).first()

    def remove_version(self):
        config_version_obj = self.get_version_by_id()
        if config_version_obj:
            config_version_obj.delete()
            return True
        return False

    def get_brake_config_version_info(self):
        return {
            "id": getattr(self, "id", "") or "",
            "former_version": getattr(self, "former_version", "") or "",
            "version": getattr(self, "version", "") or "",
            "file_uri": getattr(self, "file_uri", "") or "",
            "md5sum": getattr(self, "md5sum", "") or "",
            "message": getattr(self, "message", "") or "",
            "created_time": self.created_time,
        }
