# -*- coding: utf-8 -*-
from mongoengine.fields import StringField
from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument


class Basedata_Geo(DynamicDocument, Base_Class):
    province = StringField(default="")
    city = StringField(default="")

    meta = {'collection': 'basedata_geo'}

    @staticmethod
    def get_province_list():
        geo_list = Basedata_Geo.objects()
        province_list = [geo.province for geo in geo_list]
        province_list = list(set(province_list))
        province_list.sort()
        return province_list

    @staticmethod
    def get_city_list(province):
        geo_list = Basedata_Geo.objects(province=province)
        city_list = [geo.city for geo in geo_list]
        city_list = list(city_list)
        city_list.sort()
        return city_list

    @staticmethod
    def add_obj(province, city):
        if not Basedata_Geo.objects(province=province, city=city): Basedata_Geo.objects.create(province=province,
                                                                                               city=city)
