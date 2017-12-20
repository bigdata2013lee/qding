# -*- coding:utf-8 -*-
import datetime
from mongoengine.document import DynamicDocument
from apps.basedata.classes.Basedata_Apartment import Basedata_Apartment
from apps.basedata.classes.Basedata_BJ_App_User import Basedata_BJ_App_User
from apps.common.classes.Base_Class import Base_Class
from mongoengine.fields import ReferenceField, StringField, DateTimeField, IntField, DictField


class Brake_Password(DynamicDocument, Base_Class):
    valid_num = IntField(default=0)
    password = StringField(default="")
    start_time = DateTimeField(default=datetime.datetime.now())
    end_time = DateTimeField(default=datetime.datetime.now())
    bj_app_user = ReferenceField(Basedata_BJ_App_User, default=None)
    apartment = ReferenceField(Basedata_Apartment, default=None)
    apartment_dict = DictField(default={
        "province": "",
        "city": "",
        "project": "",
        "property_name": "",
        "build": "",
        "unit": "",
        "room": "",

        "outer_property_id": "",
        "outer_project_id": "",
        "outer_group_id": "",
        "outer_build_id": "",
    })

    meta = {'collection': 'brake_password'}

    def add_password(self, project_unit_count, brake_version, visitor, password_num):
        from apps.common.utils.sentry_date import get_str_day_by_datetime, get_distance_between_days
        from apps.common.utils.qd_encrypt import create_password, create_password_1

        start_time = get_str_day_by_datetime(self.start_time, '%Y%m%d')
        valid_num = self.valid_num if self.valid_num != -1 else 0
        count = visitor.get_count(self.apartment.project_id, self.apartment.unit_id)

        if 'V2' not in brake_version:
            province = self.apartment.province
            city = self.apartment.city
            project = self.apartment.project
            locality = "%s%s%s" % (province, city, project)
            door = "%s%s" % (self.apartment.build, self.apartment.unit)
            valid_day = get_distance_between_days(start_day=self.start_time, end_day=self.end_time)
            self.password = create_password(project_unit_count, locality, door, start_time, valid_num, count, valid_day)
        else:
            if password_num <= count: count = password_num
            self.password = create_password_1(self.apartment.unit_id, start_time, valid_num, count)
        return self.save()

    @classmethod
    def get_password(cls, str_day=None, outer_project_id=None, password=None):
        from apps.common.utils.sentry_date import get_datetime_by_str_day
        raw_query = {
            "apartment_dict.outer_project_id": outer_project_id,
            "start_time": {"$gte": get_datetime_by_str_day(str_day, str_format='%Y%m%d', index=0),
                           "$lte": get_datetime_by_str_day(str_day, str_format='%Y%m%d', index=1)},
            "password": password,
        }
        return Brake_Password.objects(__raw__=raw_query).first()
