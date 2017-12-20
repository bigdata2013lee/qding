# -*- coding:utf-8 -*-
from apps.common.api.basedata_api import Basedata_Project_Api


class Geo_Api(object):
    def get_province_list(self):
        return Basedata_Project_Api().get_province_list()

    def get_city_list(self,province):
        return Basedata_Project_Api().get_city_list_by_province(province=province)

    def get_community_list(self,province,city):
        return Basedata_Project_Api().get_project_list_by_city(province=province,city=city)