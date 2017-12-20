# -*- coding:utf-8 -*-
import json
import pickle
import traceback
import logging

from settings.const import CONST
from apps.brake.classes.Brake_Machine import Brake_Machine
from apps.brake.classes.Brake_Version import Brake_Version
from apps.common.utils import qd_result, validate
from apps.common.utils.request_api import request_bj_server
from apps.common.utils.view_tools import jsonResponse
from apps.basedata.classes.Basedata_Project import Basedata_Project
from apps.basedata.classes.Basedata_Group import Basedata_Group
from apps.basedata.classes.Basedata_Build import Basedata_Build
from apps.basedata.classes.Basedata_Unit import Basedata_Unit
from apps.basedata.classes.Basedata_Apartment import Basedata_Apartment
from apps.basedata.classes.Basedata_BJ_App_User import Basedata_BJ_App_User
from apps.common.utils.redis_client import rc

logger = logging.getLogger('qding')


class Basedata_Project_Api(object):
    '''
    @note: project api
    '''

    @jsonResponse()
    def get_province_list(self):
        '''
        @note: usefull: get province list
        @note: access url: /basedata_api/Basedata_Project_Api/get_province_list/
        @note: test demo: {}
        @return: {"err": 0, "log": "", "data": {"province_list": ["重庆", "中陲"], "flag": "Y"}, "上海板牙科技msg": ""}
        '''
        try:
            result = qd_result.get_default_result()
            project_list = Basedata_Project.objects.distinct("province")
            result['data']['province_list'] = sorted(project_list)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_city_list_by_province(self, province=None):
        '''
        @note: usefull: get city list by province
        @note: access url:/basedata_api/Basedata_Project_Api/get_city_list_by_province/
        @note: test demo:{province:"中陲"}
        @param province: province
        @return: result: {'data': {'flag': 'Y', 'city_list': ['上海']}, 'msg': '', 'err': 0, 'log': ''}
        '''
        try:
            result = qd_result.get_default_result()
            city_list = Basedata_Project.objects(province=province).distinct("city")
            result['data']['city_list'] = sorted(city_list)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_city_obj_list_by_province(self, province=None):
        '''
        @note: usefull: get city obj list by province
        @note: access url: /basedata_api/Basedata_Project_Api/get_city_obj_list_by_province/
        @note: test demo: {"province": "中陲" }
        @param province:
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            city_obj_list = []
            city_name_list = []
            project_obj_list = Basedata_Project.objects(province=province)
            for p in project_obj_list:
                if p.city not in city_name_list:
                    city_name_list.append(p.city)
                    city_obj_list.append(p)
            result['data']['city_obj_list'] = [{"city": c.city, "outer_city_id": c.outer_city_id} for c in city_obj_list]
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_city_list(self):
        '''
        @note: usefull: get city list
        @note: access url: /basedata_api/Basedata_Project_Api/get_city_list/
        @note: test demo: {}
        @return: {"err": 0, "log": "", "data": {"city_list": ["重庆", "中陲"], "flag": "Y"}, "msg": ""}
        '''
        try:
            result = qd_result.get_default_result()
            city_list = Basedata_Project.objects().distinct('city')
            result['data']['city_list'] = sorted(city_list)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_project_list_by_city(self, province=None, city=None):
        '''
        @note: usefull: get project list by city
        @note: access url: /basedata_api/Basedata_Project_Api/get_project_list_by_city/
        @note: test demo: {city:"重庆"}
        @return: {"err": 0, "log": "", "data": {"project_list": ["紫都城"], "flag": "Y"}, "msg": ""}
        '''
        try:
            result = qd_result.get_default_result()
            project_list = Basedata_Project.objects(province=province, city=city).distinct("project")
            result['data']['project_list'] = sorted(project_list)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_project_list_by_filter(self, province=None, city=None, project=None, page_no=1, page_size=0):
        '''
        @note: userfull: get project list by filter
        @note: access url: /basedata_api/Basedata_Project_Api/get_project_list_by_filter/
        @note: test demo {province:"guangdong"}
        @param province: province
        @param city: city
        @param project: project
        @param page_no: page number
        @param page_size: page size
        @return: {"err": 0, "log": "", "data": {"project_list": ["紫都城"], "flag": "Y"}, "msg": ""}
        '''
        try:
            result = qd_result.get_default_result()
            validate_page_flag, validate_page_str = validate.validate_pagination(str(page_size), str(page_no))
            if page_size and page_no and not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)

            project_list = Basedata_Project.get_project_list_by_filter(int(page_no), int(page_size),
                                                                       province=province, city=city, project=project)
            project_dict_list = [project_obj.get_project_info() for project_obj in project_list]
            result['data']['project_list'] = sorted(project_dict_list, key=lambda x: x['province'])
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': project_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_all_project_count(self):
        '''
        @note: usefull: get all project count
        @note: access url:/basedata_api/Basedata_Project_Api/get_all_project_count/
        @note: test demo: {}
        @return: {}
        '''
        try:
            result = qd_result.get_default_result()
            result['data']['project_count'] = Basedata_Project.objects(status="1").count()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def refresh_project_data(self, project_id=None):
        '''
        @note: usefull: refresh project data to cache
        @note: access url:/basedata_api/Basedata_Project_Api/refresh_project_data/1/
        @note: test demo:{project_id:"1732"}
        @param project_id:
        @return: {'err': 0, 'msg': 'success', 'log': '', 'data': {'flag': 'Y'}}
        '''
        try:
            result = qd_result.get_default_result()
            if not project_id: return qd_result.set_err_msg(result, 'project_id must be exist')

            value = pickle.dumps({"refresh_project_data": project_id})
            if not rc.sadd("update_process", value): return qd_result.set_err_msg(result, '已在刷新列表中，请稍候')
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def sync_project_data(self, project_id=None):
        '''
        @note: access url: /basedata_api/Basedata_Project_Api/sync_project_data/
        @note: test demo: {project_id:'1833'}
        @param project_id: project id
        @return: {'err': 0, 'msg': 'success', 'log': '', 'test_code': 0, 'data': {'flag': 'Y'}}
        '''
        try:
            result = qd_result.get_default_result()
            if not project_id: return qd_result.set_err_msg(result, 'project_id must be exist')

            if not rc.sadd("sync_project_data", project_id):
                return qd_result.set_err_msg(result, '已在同步队列中，请稍候')
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def find_project_by_name_from_bj(self, project_name=None):
        '''
        @note: usefull: find project by name
        @note: access url:/basedata_api/Basedata_Project_Api/find_project_by_name_from_bj/
        @note test demo:{project_name:"千丁互联"}
        @param project_name:
        @return:{'log': '', 'msg': '', 'err': 0, 'data': {'project_list': [{'projectId': '1736', 'projectName': '宁波滟澜海岸2号地块'}], 'flag': 'Y'}}
        '''
        try:
            result = qd_result.get_default_result()
            if not project_name: return qd_result.set_err_msg(result, 'project name can not be empty')

            url = CONST['bj_api_url']['api_method']['find_project_by_name'] % project_name
            project_list = request_bj_server(method_url=url, data_key='list', post_flag=False) or []

            if not project_list or not isinstance(project_list, list):
                raw_query = {"project": {"$regex": project_name}}
                ret_query = Basedata_Project.objects(__raw__=raw_query)
                project_list = [{"projectId": project_obj.outer_project_id, "projectName": project_obj.project,
                                 "cityName": project_obj.city} for project_obj in ret_query]
            result['data']['project_list'] = project_list
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_project_brake_machine_count(self, outer_project_id=None):
        '''
        @note: usefull: get project brake machine total count
        @note: access url: /basedata_api/Basedata_Project_Api/get_project_brake_machine_count/
        @note: test demo: {project_id:'1833'}
        @param outer_project_id: project id
        @return: {'msg': 'success', 'data': {'flag': 'Y', 'brake_machine_count': 1}, 'log': '', 'err': 0}
        '''
        try:
            result = qd_result.get_default_result()

            brake_machine_list = Brake_Machine.get_project_brake(outer_project_id=outer_project_id)
            result['data']['brake_machine_count'] = len(brake_machine_list)

        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_property_list_by_city(self, province, city):
        '''
        @note: usefull: get property list by city
        @note: access url: /basedata_api/Basedata_Project_Api/get_property_list_by_city/
        :param province:
        :param city:
        :return:
        '''
        try:
            result = qd_result.get_default_result()
            property_list = Basedata_Project.objects(province=province, city=city).distinct('property_name')
            result['data']['property_list'] = [pro for pro in property_list if pro]
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_property_list(self, property_name=None):
        '''
        @note: usefull get project list by property
        @note: access url: /basedata_api/Basedata_Project_Api/get_property_list/
        :param property_name:
        :return:
        '''
        try:
            result = qd_result.get_default_result()
            raw_query = {"property_name": {"$regex": property_name}}
            project_obj_list = Basedata_Project.objects(__raw__=raw_query)
            property_name_list = []
            property_list = []
            for project_obj in project_obj_list:
                if project_obj.property_name not in property_name_list:
                    property_name_list.append(project_obj.property_name)
                    property_list.append(project_obj)
            result['data']['property_list'] = [tmp_project_obj.get_project_info() for tmp_project_obj in property_list]
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_project_list_by_property(self, province=None, city=None, property_name=None):
        '''
        @note: usefull get project list by property
        @note: access url: /basedata_api/Basedata_Project_Api/get_project_list_by_property/
        :param province:
        :param city:
        :param property_name:
        :return:
        '''
        try:
            result = qd_result.get_default_result()
            if not property_name:
                project_list = Basedata_Project.objects(province=province, city=city).distinct('project')
            else:
                project_list = Basedata_Project.objects(province=province, city=city,
                                                        property_name=property_name).distinct('project')
            result['data']['project_list'] = project_list
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Basedata_Group_Api(object):
    '''
    @note: group api
    '''

    @jsonResponse()
    def get_group_list(self, province=None, city=None, project=None):
        '''
        @note: usefull: get group list
        @note: access url: /basedata_api/Basedata_Group_Api/get_group_list/
        @note: test demo: {province:"重庆",city:"重庆",project:"千丁"}
        @param province: province
        @param city: city
        @param project: project
        @return: {"err": 0, "log": "", "data": {"group_list": ["紫都城"], "flag": "Y"}, "msg": ""}
        '''
        try:
            result = qd_result.get_default_result()

            group_obj = Basedata_Group(province=province, city=city, project=project)
            group_list = group_obj.get_group_list_by_project()

            result['data']['group_list'] = sorted(group_list)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_group_list_by_filter(self, province=None, city=None, project=None, group=None,
                                 project_id=None, page_no=1, page_size=0):
        '''
        @note: access url: /basedata_api/Basedata_Group_Api/get_group_list_by_filter/
        @param province: province
        @param city: city
        @param project: project
        @param group: group
        @param project_id: project id
        @param page_no: page number
        @param page_size: page size
        @return: 
        '''
        try:
            result = qd_result.get_default_result()
            validate_page_flag, validate_page_str = validate.validate_pagination(str(page_size), str(page_no))
            if page_size and page_no and not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)

            if project_id: project_id = int(project_id)

            group_list = Basedata_Group(province=province, city=city, project=project, group=group,
                                        project_id=project_id).get_group_list_by_filter(int(page_no), int(page_size))

            result['data']['group_list'] = [group_obj.get_group_info() for group_obj in group_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': group_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Basedata_Build_Api(object):
    '''
    @note: build operator class
    '''

    @jsonResponse()
    def get_build_list(self, province=None, city=None, project=None, group=None):
        '''
        @note access url: /basedata_api/Basedata_Build_Api/get_build_list/
        @note test demo:{"province":"xx", "city":"xx", "project":"xx", "group":"xx"}
        @param province: province
        @param city: city
        @param project: project
        @param group: group
        @return:
        '''
        try:
            result = qd_result.get_default_result()

            build_obj = Basedata_Build(province=province, city=city, project=project, group=group)
            build_list = build_obj.get_build_list_by_project_or_group()

            result['data']['build_list'] = sorted(build_list)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_build_list_by_filter(self, province=None, city=None, project=None, group=None, build=None,
                                 project_id=None, group_id=None, page_no=1, page_size=0):
        '''
        @note: access url: /basedata_api/Basedata_Build_Api/get_build_list_by_filter/
        @param province: province
        @param city: city
        @param project: project
        @param group: group
        @param build: build
        @param project_id: project_id
        @param group_id: group_id
        @param page_no: page number
        @param page_size: page size
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            validate_page_flag, validate_page_str = validate.validate_pagination(str(page_size), str(page_no))
            if page_size and page_no and not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)

            if project_id: project_id = int(project_id)
            if group_id: group_id = int(group_id)

            build_list = Basedata_Build(province=province, city=city, project=project, group=group,
                                        build=build, project_id=project_id,
                                        group_id=group_id).get_build_list_by_filter(int(page_no), int(page_size))
            result['data']['build_list'] = [build_obj.get_build_info() for build_obj in build_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': build_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Basedata_Unit_Api(object):
    '''
    @note: unit operator class
    '''

    @jsonResponse()
    def get_unit_list(self, province=None, city=None, project=None, group=None, build=None):
        '''
        @note access url: /basedata_api/Basedata_Unit_Api/get_unit_list/
        @note test demo:{"province":"xx", "city":"xx", "project":"xx", "group":"xx", "build":"xx"}
        @param province: province
        @param city: city
        @param project: project
        @param group: group
        @param build: build
        @return:
        '''
        try:
            result = qd_result.get_default_result()

            unit_obj = Basedata_Unit(province=province, city=city, project=project, group=group, build=build)
            unit_list = unit_obj.get_unit_list_by_build()

            result['data']['unit_list'] = sorted(unit_list)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_unit_list_by_filter(self, province=None, city=None, project=None, group=None, build=None, unit=None,
                                project_id=None, group_id=None, build_id=None, page_no=1, page_size=0):
        '''
        @note: access url: /basedata_api/Basedata_Unit_Api/get_unit_list_by_filter/
        @param province: province
        @param city: city
        @param project: project
        @param group: group
        @param build: build
        @param unit: unit
        @param project_id: project id
        @param group_id: group id
        @param build_id: build id
        @param page_no: page number
        @param page_size: page size
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            validate_page_flag, validate_page_str = validate.validate_pagination(str(page_size), str(page_no))
            if page_size and page_no and not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)

            if project_id: project_id = int(project_id)
            if group_id: group_id = int(group_id)
            if build_id: build_id = int(build_id)

            unit_list = Basedata_Unit(province=province, city=city, project=project, group=group, build=build,
                                      unit=unit, project_id=project_id, group_id=group_id,
                                      build_id=build_id).get_unit_list_by_filter(int(page_no), int(page_size))
            result['data']['unit_list'] = [unit_obj.get_unit_info() for unit_obj in unit_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': unit_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Basedata_Apartment_Api(object):
    """
    @note: 房屋的相关操作
    """

    @jsonResponse()
    def get_apartment_by_filter(self, province=None, city=None, project=None, group=None, build=None, unit=None,
                                room=None, project_id=None, group_id=None, build_id=None, unit_id=None,
                                room_id=None, outer_project_id=None, page_size=0, page_no='1'):
        """
        @note: 访问url： /basedata_api/Basedata_Apartment_Api/get_apartment_by_filter/1/
        @param province: province
        @param city: city
        @param project: project
        @param group: group
        @param build: build
        @param unit: unit
        @param room: room
        @param project_id: project id
        @param group_id:group id
        @param build_id: build id
        @param unit_id: unit_id
        @param room_id: outer room id
        @param outer_project_id： outer project id
        @param page_size: 每页的数目
        @param page_no: 具体哪一页  
        @return: {'err': 0, 'msg': '', 'log': '', 'data': {'pagination': {'page_size': 50, 'total_count': 29, 'page_no': 1}, 'apartment_list': [{'name': '孙鹏', 'id': '5642bdf3c0d2071ea6d7fb33', 'room_id': '712991', 'build': '1', 'province': '中陲', 'community': '千丁嘉园', 'unit': '1', 'city': '中陲', 'room': '101'}]}}
        """
        try:
            result = qd_result.get_default_result()
            validate_page_flag, validate_page_str = validate.validate_pagination(str(page_size), str(page_no))
            if page_size and page_no and not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)
            if project_id: project_id = int(project_id)
            if group_id: group_id = int(group_id)
            if build_id: build_id = int(build_id)
            if unit_id: unit_id = int(unit_id)
            apartment_obj = Basedata_Apartment(province=province, city=city, project=project, group=group, build=build,
                                               unit=unit, room=room, project_id=project_id, group_id=group_id,
                                               build_id=build_id, unit_id=unit_id, outer_room_id=room_id,
                                               outer_project_id=outer_project_id)
            apartment_list = apartment_obj.get_apartment_by_filter(int(page_size), int(page_no))
            result['data']['apartment_list'] = [apartment_obj.get_apartment_info() for apartment_obj in apartment_list]
            result['data']['pagination'] = {
                'page_no': int(page_no),
                'page_size': int(page_size),
                'total_count': apartment_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_room_list(self, province=None, city=None, project=None, group=None, build=None, unit=None):
        '''
        @note: access url:/basedata_api/Basedata_Apartment_Api/get_room_list/1/
        @param province: province
        @param city: city
        @param project: project
        @param group: group
        @param build: build
        @param unit: unit
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            province_flag, province_str = validate.validate_province(province)
            if not province_flag: return qd_result.set_err_msg(result, province_str)

            city_flag, city_str = validate.validate_city(city)
            if not city_flag: return qd_result.set_err_msg(result, city_str)

            project_flag, project_str = validate.validate_project(project)
            if not project_flag: return qd_result.set_err_msg(result, project_str)

            group_flag, group_str = validate.validate_group(group)
            if not group_flag: return qd_result.set_err_msg(result, group_str)

            build_flag, build_str = validate.validate_build(build)
            if not build_flag: return qd_result.set_err_msg(result, build_str)

            unit_flag, unit_str = validate.validate_unit(unit)
            if not unit_flag: return qd_result.set_err_msg(result, unit_str)

            result['data']['room_list'] = sorted(
                Basedata_Apartment(province=province, city=city, project=project, group=group,
                                   build=build, unit=unit).get_room_list())
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Basedata_Bj_App_User_Api(object):
    '''
    @note: bj app user api
    '''

    @jsonResponse()
    def get_app_user_bind_room_list(self, phone=None, sorted_direction=''):
        '''
        @note: usefull: get app user bind room list
        @note: access url:/basedata_api/Basedata_Bj_App_User_Api/get_app_user_bind_room_list/1/
        @note: test demo:{phone:"12345678901"}
        @param phone: phone
        @param sorted_direction: sorted_direction
        @return: {'room_list': ['重庆洪泉洪逸新村11洪逸新村', '重庆凯美华美时代城11华美时代城', '重庆水晶郦城静苑110102', '西藏中陲千丁互联组团1G1千丁用户', '西藏中陲地产大院组团11-change605121单元1012', '西藏中陲地产大院3组团421单元1021', '北京长楹天街写字楼东1#公寓东1#公寓-1号楼11单元/10层/1001'], 'data': {'flag': 'Y'}, 'msg': 'success', 'log': '', 'err': 0}
        '''
        try:
            result = qd_result.get_default_result()
            result['data']['room_list'] = []

            app_user_list, ret_str = Basedata_BJ_App_User(phone=str(phone)).get_app_user_by_phone(1498724908)
            if not app_user_list: return qd_result.set_err_msg(result, ret_str)

            app_user_list = [app_user_list] if isinstance(app_user_list, Basedata_BJ_App_User) else app_user_list
            room_list = []
            for app_user in app_user_list:
                for room_data in app_user.room_data_list:
                    room_info = "%s%s%s%s%s%s%s" % (room_data['province'], room_data['city'], room_data['project'],
                                                    room_data['group'], room_data['build'], room_data['unit'],
                                                    room_data['room'])
                    if room_info: room_list.append(room_info)

            room_list = list(set(room_list))
            room_list = sorted(room_list)
            if '-' in sorted_direction:
                room_list = room_list[::-1]
            result['data']['room_list'] = room_list
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_app_user_bind_door_list(self, phone=None):
        '''
        @note: usefull: get app user bind door list
        @note: access url:/basedata_api/Basedata_Bj_App_User_Api/get_app_user_bind_door_list/1/
        @note: test demo:{phone:"18392130738"}
        @param phone: phone
        @return: {'msg': 'success', 'log': '', 'err': 0, 'data': {'flag': 'Y', 'door_list': [{'updated_time': 1450153208,'direction': 'I', 'open_time': '500', 'bluetooth_rssi': '-85', 'online_status': 0, 'wifi_rssi': '-80', 'command': '0', 'city': '重庆', 'heart_time': 24, 'position_str': '紫都城105门岗通道1入', 'province': '重庆', 'mac': '883B8B038376', 'gate_name': '105门岗通道1', 'position': {'province': '重庆', 'city': '重庆', 'outer_city_id': '3', 'project_list': [{'project': '紫都城', 'outer_project_id': '64'}], 'level': 2}, 'version': 'V1.0.3', 'is_monit': 0, 'id': '566f94f82c923a33b32753ef'}]}}
        '''
        try:
            result = qd_result.get_default_result()
            result['data']['door_list'] = []

            app_user_list, ret_str = Basedata_BJ_App_User(phone=str(phone)).get_app_user_by_phone(1498724908)
            if not app_user_list: return qd_result.set_err_msg(result, ret_str)

            app_user_list = [app_user_list] if isinstance(app_user_list, Basedata_BJ_App_User) else app_user_list
            door_list = []
            for app_user in app_user_list:
                door_list += app_user.get__bind_door_list()
            result['data']['door_list'] = door_list
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_app_user_can_open_door(self, phone=None, sorted_field='updated_time', sorted_direction=''):
        '''
        @note: usefull: get app user can open door by phone
        @note: access url:/basedata_api/Basedata_Bj_App_User_Api/get_app_user_can_open_door/1/
        @note: test demo:{phone:"12345678901"}
        @param phone: phone
        @param sorted_field: sorted_field
        @param sorted_direction: sorted_direction
        @return: {'msg': 'success', 'log': '', 'err': 0, 'data': {'flag': 'Y', 'door_list': [{'updated_time': 1450153208,'direction': 'I', 'open_time': '500', 'bluetooth_rssi': '-85', 'online_status': 0, 'wifi_rssi': '-80', 'command': '0', 'city': '重庆', 'heart_time': 24, 'position_str': '紫都城105门岗通道1入', 'province': '重庆', 'mac': '883B8B038376', 'gate_name': '105门岗通道1', 'position': {'province': '重庆', 'city': '重庆', 'outer_city_id': '3', 'project_list': [{'project': '紫都城', 'outer_project_id': '64'}], 'level': 2}, 'version': 'V1.0.3', 'is_monit': 0, 'id': '566f94f82c923a33b32753ef'}]}}
        '''
        try:
            result = qd_result.get_default_result()
            result['data']['door_list'] = []

            app_user_list, ret_str = Basedata_BJ_App_User(phone=str(phone)).get_app_user_by_phone(1498724908)
            if not app_user_list: return qd_result.set_err_msg(result, ret_str)

            app_user_list = [app_user_list] if isinstance(app_user_list, Basedata_BJ_App_User) else app_user_list
            door_list = []
            for app_user in app_user_list:
                door_list += app_user.get_can_open_brake()

            if not door_list: return qd_result.set_err_msg(result, '')

            ret_list = []
            mac_list = []
            for door in door_list:
                if door['mac'] not in mac_list:
                    ret_list.append(door)
                    mac_list.append(door['mac'])

            door_list = sorted(ret_list, key=lambda x: x[sorted_field])
            if sorted_direction == '-': door_list = door_list[::-1]
            result['data']['door_list'] = door_list
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_app_user_can_open_door_list(self, outer_app_user_id=None):
        '''
        @note: usefull: get app user can open door list by outer app user id
        @note: access url:/basedata_api/Basedata_Bj_App_User_Api/get_app_user_can_open_door_list/1/
        @note: test demo:{outer_app_user_id:"8aa57dca4fcfaf9f01508423b56c010a"}
        @param outer_app_user_id: outer app user id
        @return: {'log': '', 'err': 0, 'msg': 'success', 'data': { 'flag': 'Y', 'door_list':[{'direction': 'I', 'unit': '', 'build': '', 'gate': '地面', 'wifi_rssi': '-80', 'mac': '883B8B038B19', 'province': '重庆', 'open_time': '500', 'version': 'V1.0.3', 'brake_type': '', 'bluetooth_rssi': '-80', 'community': '水晶郦城', 'city': '重庆'}],'room_info': [{'project_group_build_unit_id': 692502151, 'password_num': 15000}]}}
        '''
        try:
            result = qd_result.get_default_result()

            result['data']['door_list'] = []

            door_list, room_info = Basedata_BJ_App_User.get_can_open_brake_by_outer_app_user_id(oaud=str(outer_app_user_id))
            if not door_list: return qd_result.set_err_msg(result, "可开门列表为空")

            result['data']['door_list'] = door_list
            result['data']['room_info'] = room_info
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_app_user_can_open_door_list(self, phone=None, brake_mac_list=[]):
        '''
        @note: usefull: set app user can open door list
        @note: access url:/basedata_api/Basedata_Bj_App_User_Api/set_app_user_can_open_door_list/1/
        @note: test demo:{"phone":"12345678901","brake_mac_list":'["112233445566"]'}
        @param phone: phone
        @param brake_mac_list: brake mac list
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            brake_mac_list = json.loads(brake_mac_list) if isinstance(brake_mac_list, str) else brake_mac_list
            if not isinstance(brake_mac_list, list): return qd_result.set_err_msg(result, 'brake_mac_list must list')

            app_user_list, ret_str = Basedata_BJ_App_User(phone=str(phone)).get_app_user_by_phone(1498724908)
            if not app_user_list: return qd_result.set_err_msg(result, ret_str)

            app_user_list = [app_user_list] if isinstance(app_user_list, Basedata_BJ_App_User) else app_user_list
            bind_door_list = []
            for mac in brake_mac_list:
                db_brake_machine = Brake_Machine.get_brake_by_mac(mac=mac)
                if db_brake_machine and db_brake_machine not in bind_door_list:
                    bind_door_list.append({"id": str(db_brake_machine.id)})

            for app_user in app_user_list:
                app_user.set_bind_door_list(bind_door_list)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def delete_app_user_can_open_door_list(self, phone=None, brake_mac_list=[]):
        '''
        @note: delete app user can open door list
        @note: access method: /basedata_api/Basedata_Bj_App_User_Api/delete_app_user_can_open_door_list/
        @param phone:phone
        @param brake_mac_list:brake mac list
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            brake_mac_list = json.loads(brake_mac_list) if isinstance(brake_mac_list, str) else brake_mac_list
            if not isinstance(brake_mac_list, list): return qd_result.set_err_msg(result, 'brake_mac_list must be list')

            app_user_list, ret_str = Basedata_BJ_App_User(phone=str(phone)).get_app_user_by_phone()
            if not app_user_list: return qd_result.set_err_msg(result, ret_str)

            app_user_list = [app_user_list] if isinstance(app_user_list, Basedata_BJ_App_User) else app_user_list
            delete_door_list = []
            for mac in brake_mac_list:
                mac = str(mac).strip()
                db_brake_machine = Brake_Machine.objects(mac=mac, status="1").first()
                if db_brake_machine and db_brake_machine not in delete_door_list:
                    delete_door_list.append({"id": str(db_brake_machine.id)})
            for app_user in app_user_list:
                app_user.delete_bind_door_list(delete_door_list)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_app_user_can_pass_project(self, outer_project_id=None, phone=None, method="set_bind_door_list"):
        '''
        @note: access url: /basedata_api/Basedata_Bj_App_User_Api/set_app_user_can_pass_project/
        @note: demo: {"outer_project_id":"1879", "phone":"18392130738", "method": "set_bind_door_list"}
        @param outer_project_id: outer project id
        @param phone: phone
        @param method: set method, only can be "set_bind_door_list" or "delete_bind_door_list"
        @return: {'err': 0, 'msg': 'success', 'log': '', 'data': {'flag': 'Y'}}
        '''
        try:
            result = qd_result.get_default_result()
            project_id_check_flag, project_id_check_str = validate.validate_outer_project_id(outer_project_id)
            if not project_id_check_flag: return qd_result.set_err_msg(result, project_id_check_str)

            method_check_flag, method_check_str = validate.validate_set_app_user_bind_door_method(method)
            if not method_check_flag: return qd_result.set_err_msg(result, method_check_str)

            app_user_list, ret_str = Basedata_BJ_App_User(phone=str(phone)).get_app_user_by_phone(1498724908)
            if not app_user_list: return qd_result.set_err_msg(result, ret_str)

            app_user_list = [app_user_list] if isinstance(app_user_list, Basedata_BJ_App_User) else app_user_list

            brake_machine_list = Brake_Machine.get_project_brake(outer_project_id=str(outer_project_id))
            for db_app_user in app_user_list:
                invoke_method = getattr(db_app_user, method)
                invoke_method(brake_machine_list)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def clear_app_user_can_open_door(self, phone_list=[]):
        '''
        @note: userfull: clear app user can open door
        @note: access url: /basedata_api/Basedata_Bj_App_User_Api/clear_app_user_can_open_door/
        @note: test demo: {phone_list: '["12345678901","12345678902"]'}
        :param phone_list:
        :return: {'err': 0, 'log': '', 'msg': 'fail', 'data': {'flag': 'N', 'clear_failed_phone_list':[{"phone":"12345678901","reason":"phone not exists"}]}}
        '''
        try:
            result = qd_result.get_default_result()
            phone_list = json.loads(phone_list) if isinstance(phone_list, str) else phone_list

            clear_failed_phone_list = []
            for phone in phone_list:
                ret = {}
                app_user_list, ret_str = Basedata_BJ_App_User(phone=str(phone)).get_app_user_by_phone(1498724908)
                if not app_user_list:
                    ret.update({
                        "phone": phone,
                        "reason": ret_str,
                    })
                    clear_failed_phone_list.append(ret)
                    continue
                for app_user in app_user_list:
                    app_user.clear_door_list()
            if clear_failed_phone_list:
                result['data']['flag'] = 'N'
                result['data']['clear_failed_phone_list'] = clear_failed_phone_list
                return result
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_app_user_id(self, outer_app_user_id=None):
        '''
        @note: usefull: get app user id
        @note: access url: /basedata_api/Basedata_Bj_App_User_Api/get_app_user_id/
        @note: test demo {"outer_app_user_id":"2c90806a54a950050154c7a26b8c03f7"}
        @param outer_app_user_id: outer app user id
        @return: {'err': 0, 'log': '', 'msg': 'success', 'data': {'app_user_id': 3900903306, 'flag': 'Y'}}
        '''
        try:
            result = qd_result.get_default_result()

            app_user, ret_str = Basedata_BJ_App_User(
                outer_app_user_id=str(outer_app_user_id)).get_app_user_by_outer_app_user_id(1498724908)
            if not app_user: return qd_result.set_err_msg(result, ret_str)

            app_user_id = app_user.get_app_user_id()
            if not app_user_id: return qd_result.set_err_msg(result, 'no user id')

            result['data']['app_user_id'] = app_user_id
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_app_user_room_list(self, phone=None):
        '''
        @note: usefull: set app user room list
        @note: access url: /basedata_api/Basedata_Bj_App_User_Api/set_app_user_room_list/
        @note: test demo {"phone":"12345678901"}
        @param phone: phone
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            rc.sadd("update_app_user", phone)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_app_user_room_list_now(self, phone=None):
        '''
        @note: usefull: set app user room list
        @note: access url: /basedata_api/Basedata_Bj_App_User_Api/set_app_user_room_list_now/
        @note: test demo {"phone":"12345678901"}
        @param phone: phone
        @return:
        '''
        try:
            result = qd_result.get_default_result()

            app_user_list, ret_str = Basedata_BJ_App_User(phone=str(phone)).get_app_user_by_phone()
            if not app_user_list: return qd_result.set_err_msg(result, ret_str)

            app_user_list = [app_user_list] if isinstance(app_user_list, Basedata_BJ_App_User) else app_user_list
            for app_user in app_user_list:
                app_user.set_app_user_from_bj(app_user.outer_app_user_id)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_app_user_by_filter(self, province=None, city=None, project=None, outer_app_user_id=None,
                               app_user_id=None, phone=None, page_no=1, page_size=30):
        '''
        @note: access url: /basedata_api/Basedata_Bj_App_User_Api/get_app_user_by_filter/
        @param province:
        @param city:
        @param project:
        @param outer_app_user_id:
        @param app_user_id:
        @param phone:
        @param page_no
        @param page_size
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            regex_dict = {
                "outer_app_user_id": outer_app_user_id,
                "app_user_id": app_user_id,
                "phone": phone,
            }
            pos_dict = {
                "province": province,
                "city": city,
                "project": project
            }
            db_app_user_list = Basedata_BJ_App_User.get_user_by_filter(pos_dict=pos_dict,
                                                                       regex_dict=regex_dict,
                                                                       page_no=int(page_no),
                                                                       page_size=int(page_size))
            result['data']['app_user_list'] = [db_app_user.get_app_user_info() for db_app_user in db_app_user_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': db_app_user_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def check_brake_firmware_version(self, outer_app_user_id=None):
        '''
        @note: usefull: check brake firmware version
        @note: access url: /basedata_api/Basedata_Bj_App_User_Api/check_brake_firmware_version/
        @note: test demo: {"outer_app_user_id":"2c90806a54a950050154c7a26b8c03f7"}
        @param outer_app_user_id: outer app user id
        @return: {'data': {'flag': 'Y', 'version_info_list': [{'project': '中陲中陲千丁-嘉园', 'version_info': {'lowest_version_code': 110,'version_code': 211, 'file_uri': 'https://www.qding.cloud/uploads/brake/rom/test.v1.0.txt', 'md5sum': 'd41d8cd98f00b204e9800998ecf8427e', 'version': 'V2.1.1'}}]}, 'msg': 'success', 'err': 0, 'test_code': 0, 'log': ''}
        '''
        try:
            result = qd_result.get_default_result()

            version_info_list, ret_str = Basedata_BJ_App_User.get_version_info_list(outer_app_user_id=str(outer_app_user_id))

            if not version_info_list: return qd_result.set_err_msg(result, ret_str)

            result['data']['version_info_list'] = version_info_list
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_brake_firmware_version(self, version=None, mac=None):
        '''
        @note: usefull: set brake firmware version
        @note: access url: /basedata_api/Basedata_Bj_App_User_Api/set_brake_firmware_version/
        @note: test demo: {"version": "V1.1", "mac":"112233445566"}
        @param version: version
        @param mac: mac
        @return: {'log': '', 'err': 0, 'test_code': 0, 'data': {'flag': 'Y'}, 'msg': 'success'}
        '''
        try:
            result = qd_result.get_default_result()
            mac = mac.replace(":", "").replace(" ", "")

            brake_version = Brake_Version(version=version).get_version_by_version()
            if not brake_version:
                return qd_result.set_err_msg(result, "the version does not exist")

            brake = Brake_Machine.objects(mac=mac, status="1").first()
            if not brake:
                return qd_result.set_err_msg(result, 'the brake machine does not exist ')

            # brake.version = brake_version
            brake.firmware_version = brake_version.version
            brake.save()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result
