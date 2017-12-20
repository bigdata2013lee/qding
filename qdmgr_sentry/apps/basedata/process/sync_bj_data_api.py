# --*-- coding:utf-8 --*--
import os
import logging
import pickle

from apps.const import CONST
from xml.etree import ElementTree as ET
from apps.common.utils.qd_email import send_email
from apps.basedata.process.get_bj_data_scheme import down_xml

from apps.web.classes.Web_User import Web_User
from apps.brake.classes.Brake_Machine import Brake_Machine
from apps.basedata.classes.Basedata_Project import Basedata_Project
from apps.basedata.classes.Basedata_Group import Basedata_Group
from apps.basedata.classes.Basedata_Build import Basedata_Build
from apps.basedata.classes.Basedata_Unit import Basedata_Unit
from apps.basedata.classes.Basedata_Apartment import Basedata_Apartment

from apps.common.utils.redis_client import rc

logger = logging.getLogger('qding')


def get_attr(element, attr):
    if not element: return ""
    return element.find(attr).text.strip() if element.find(attr) is not None and element.find(attr).text else ""


def get_element_data(element, *attrs):
    ret = []
    for attr in attrs:
        value = get_attr(element, attr)
        ret.append(value)
    return ret


def check_value_empty(attr_dict, node_name):
    for k, v in attr_dict.items():
        if not v: return False, "节点%s下存在%s为空的情况" % (node_name, k)
    return True, ""


def find_dict_member_in_list(dict_list, key, value):
    for member in dict_list:
        if key in member.keys() and member.get(key) == value: return member
    return None


def get_project_data(qd_property, project):
    property_name, outer_property_id = get_element_data(qd_property, 'shortName', 'id')
    province, city, project, outer_city_id, outer_project_id = get_element_data(project,
                                                                                'provinceName', 'cityName', 'name',
                                                                                'cityId', 'id')
    province = province.replace("省", "").replace("市", "")
    city = city.replace("市", "")

    ret, ret_str = check_value_empty({
        "id": outer_project_id, "name": project, "cityId": outer_city_id, "cityName": city, "provinceName": province,
    }, "project")

    if not ret: return {}, ret_str

    return {
               "province": province, "city": city, "property_name": property_name, "project": project,
               "outer_city_id": outer_city_id, "outer_property_id": outer_property_id,
               "outer_project_id": outer_project_id
           }, ""


def get_group_data(project_dict, group_list):
    ret_str = ""
    group_dict_list = []
    for group_element in group_list:
        outer_group_id, group = get_element_data(group_element, 'id', 'name')
        _ret, _ret_str = check_value_empty({"id": outer_group_id, "name": group}, "communityRegion")
        if not _ret:
            ret_str = "%s\n%s" % (ret_str, _ret_str) if ret_str else _ret_str
        else:
            group_dict = {}
            group_dict.update(project_dict)
            group_dict.update({"outer_group_id": outer_group_id, "group": group})
            group_dict_list.append(group_dict)
    return group_dict_list, ret_str


def get_build_data(building_list, project_dict, group_dict_list):
    ret_str = ""
    build_dict_list = []
    building_group_id_set = set()
    for build_element in building_list:
        building_group_id_set.add(get_attr(build_element, "groupId"))
        outer_group_id, outer_build_id, build = get_element_data(build_element, 'groupId', 'id', 'name')
        build = build.replace("栋", "").replace("单元", "")
        _ret, _ret_str = check_value_empty({"id": outer_build_id, "name": build}, "building")
        if not _ret:
            ret_str = "%s\n%s" % (ret_str, _ret_str) if ret_str else _ret_str
            continue

        build_dict = {}
        if outer_group_id and group_dict_list:
            group_dict = find_dict_member_in_list(group_dict_list, "outer_group_id", outer_group_id)
            if group_dict is None:
                tmp_str = "building中的groupId:%s在communityRegionList不存在" % outer_group_id
                ret_str = "%s\n%s" % (ret_str, tmp_str) if ret_str else tmp_str
                continue
            build_dict.update(group_dict)
            build_dict.update({"outer_build_id": outer_build_id, "build": build})
            build_dict_list.append(build_dict)
        else:
            build_dict.update(project_dict)
            build_dict.update({"outer_group_id": "", "group": "", "outer_build_id": outer_build_id, "build": build})
            build_dict_list.append(build_dict)
    if {''} < building_group_id_set:
        build_dict_list = []
        tmp_str = "buildingList存在部分groupId为空的情况"
        ret_str = "%s\n%s" % (ret_str, tmp_str) if ret_str else tmp_str
    return build_dict_list, ret_str


def get_unit_room_data(room_list, build_dict_list):
    ret_str = ""
    room_dict_list = []
    unit_dict_list = []
    for room_element in room_list:
        outer_build_id, outer_room_id, unit, room = get_element_data(room_element, 'buildingId', 'id', 'unit', 'name')
        if not unit: unit = '1'
        unit = unit.replace("栋", "").replace("单元", "")
        room = room.replace("栋", "").replace("单元", "")
        _ret, _ret_str = check_value_empty({"id": outer_room_id, "name": room, "buildingId": outer_build_id}, "room")
        if not _ret:
            ret_str = "%s\n%s" % (ret_str, _ret_str) if ret_str else _ret_str
            continue
        build_dict = find_dict_member_in_list(build_dict_list, "outer_build_id", outer_build_id)
        if not build_dict:
            tmp_str = "room中的buildingId:%s在buildList中不存在" % outer_build_id
            ret_str = "%s\n%s" % (ret_str, tmp_str) if ret_str else tmp_str
            continue
        room_dict = {}
        unit_dict = {}
        unit_dict.update(build_dict)
        room_dict.update(build_dict)
        unit_dict.update({"unit": unit})
        room_dict.update({"unit": unit, "room": room, "outer_room_id": outer_room_id})
        if unit_dict not in unit_dict_list: unit_dict_list.append(unit_dict)
        room_dict_list.append(room_dict)
    return unit_dict_list, room_dict_list, ret_str


def update_web_user_cache():
    for k in rc.cnn.keys("api_cache:Web_User.get_access_project_info*"): rc.cnn.delete(k)
    for user in Web_User.objects(__raw__={"area":{"$ne": None}}): Web_User.get_access_project_info(user_obj=user)


def update_project_name(new_project_name, old_project_obj):
    raw_query = {
        "position.province": old_project_obj.province,
        "position.city": old_project_obj.city,
        "position.project_list.project": old_project_obj.project,
    }
    for brake in Brake_Machine.objects(__raw__=raw_query):
        position = getattr(brake, "position", {}) or {}
        project_list = position.get("project_list", []) or []
        for i in range(len(project_list)):
            project = project_list[i].get("project", "")
            if project == old_project_obj.project:
                project_list[i].update({"project": new_project_name})
        position.update({"project_list": project_list})
        brake.position = position
        brake.save()
    name = "%sinit_project_data" % old_project_obj.outer_project_id
    rc.cnn.delete(name)


def check_project_name_change(outer_project_id, project):
    project_obj = Basedata_Project.objects(outer_project_id=outer_project_id).first()
    if project_obj and project_obj.project != project:
        return True, project_obj
    else:
        return False, None


def _get_xml_data(xml_name, xml_dir=CONST['xml_dir']):
    tree = ET.parse(os.path.join(xml_dir, xml_name))
    root = tree.getroot()
    qd_property = root.find('./property')
    project = root.find('./project')
    group_list = root.findall('./communityRegionList/communityRegion')
    building_list = root.findall('./buildingList/building')
    room_list = root.findall('./roomList/room')
    if not project:
        email_content = '%s-同步失败，无法获得项目信息' % xml_name
    elif not building_list:
        email_content = '%s-同步失败，缺少楼栋数据' % xml_name
    elif not room_list:
        email_content = '%s-同步失败，缺少房间数据' % xml_name
    else:
        project_dict, email_content = get_project_data(qd_property, project)
        if project_dict:
            group_dict_list, email_content = get_group_data(project_dict, group_list)
            build_dict_list, ret_str = get_build_data(building_list, project_dict, group_dict_list)
            if ret_str: email_content = "%s\n%s" % (email_content, ret_str) if email_content else ret_str
            if build_dict_list:
                unit_dict_list, room_dict_list, ret_str = get_unit_room_data(room_list, build_dict_list)
                if ret_str: email_content = "%s\n%s" % (email_content, ret_str) if email_content else ret_str
                if room_dict_list:
                    return email_content, project_dict, group_dict_list, build_dict_list, unit_dict_list, room_dict_list
    return email_content, {}, [], [], [], []


def set_collection_id(project_obj):
    def _get_tmp_cache_key(data_type, **kwargs):
        key = ''
        if data_type == 'group':
            key = 'group_%s_%s' % (kwargs['outer_project_id'], kwargs['outer_group_id'])
        elif data_type == 'build':
            key = 'build_%s_%s_%s' % (kwargs['outer_project_id'], kwargs['outer_group_id'],
                                      kwargs['outer_build_id'])
        elif data_type == 'unit':
            key = 'unit_%s_%s_%s_%s' % (kwargs['outer_project_id'], kwargs['outer_group_id'],
                                        kwargs['outer_build_id'], kwargs['unit'])
        return key

    def _get_tmp_cache_data(tmp_data_cache, data_type, **kwargs):
        key = _get_tmp_cache_key(data_type, **kwargs)
        data_obj = tmp_data_cache.get(key, None)
        if not data_obj:
            if data_type == 'group':
                data_obj = Basedata_Group.objects(outer_project_id=kwargs['outer_project_id'],
                                                  outer_group_id=kwargs['outer_group_id']).first()
            elif data_type == 'build':
                data_obj = Basedata_Build.objects(outer_project_id=kwargs['outer_project_id'],
                                                  outer_group_id=kwargs['outer_group_id'],
                                                  outer_build_id=unit_obj.kwargs['outer_build_id']).first()
            elif data_type == 'unit':
                data_obj = Basedata_Unit.objects(outer_project_id=kwargs['outer_project_id'],
                                                 outer_group_id=kwargs['outer_group_id'],
                                                 outer_build_id=kwargs['outer_build_id'],
                                                 unit=kwargs['unit']).first()
        if data_obj and key not in tmp_data_cache:
            tmp_data_cache[key] = data_obj
        return data_obj

    def _set_tmp_cache_data(tmp_data_cache, data_type, data_obj, **kwargs):
        key = _get_tmp_cache_key(data_type, **kwargs)
        if data_obj and key not in tmp_data_cache:
            tmp_data_cache[key] = data_obj

    group_list = Basedata_Group.objects(outer_project_id=project_obj.outer_project_id)
    build_list = Basedata_Build.objects(outer_project_id=project_obj.outer_project_id)
    unit_list = Basedata_Unit.objects(outer_project_id=project_obj.outer_project_id)
    room_list = Basedata_Apartment.objects(outer_project_id=project_obj.outer_project_id)
    project_obj.room_num = room_list.count() if room_list.count() else 1500
    project_obj.unit_num = unit_list.count()
    project_obj.save()

    tmp_cache = {}

    for group_obj in group_list:
        group_obj.project_id = project_obj.project_id
        group_obj.save()

        _set_tmp_cache_data(tmp_cache, 'group', group_obj,
                            outer_project_id=group_obj.outer_project_id,
                            outer_group_id=group_obj.outer_group_id)

    for build_obj in build_list:
        build_obj.project_id = project_obj.project_id
        group_obj = _get_tmp_cache_data(tmp_cache, 'group',
                                        outer_project_id=build_obj.outer_project_id,
                                        outer_group_id=build_obj.outer_group_id)
        build_obj.group_id = getattr(group_obj, 'group_id', 0) or 0
        build_obj.save()
        _set_tmp_cache_data(tmp_cache, 'build', build_obj,
                            outer_project_id=build_obj.outer_project_id,
                            outer_group_id=build_obj.outer_group_id,
                            outer_build_id=build_obj.outer_build_id)

    for unit_obj in unit_list:
        unit_obj.project_id = project_obj.project_id
        group_obj = _get_tmp_cache_data(tmp_cache, 'group',
                                        outer_project_id=unit_obj.outer_project_id,
                                        outer_group_id=unit_obj.outer_group_id)
        build_obj = _get_tmp_cache_data(tmp_cache, 'build',
                                        outer_project_id=unit_obj.outer_project_id,
                                        outer_group_id=unit_obj.outer_group_id,
                                        outer_build_id=unit_obj.outer_build_id)
        unit_obj.group_id = getattr(group_obj, 'group_id', 0) or 0
        unit_obj.build_id = getattr(build_obj, 'build_id', 0) or 0
        unit_room_num = room_list.filter(outer_project_id=unit_obj.outer_project_id,
                                         outer_group_id=unit_obj.outer_group_id,
                                         outer_build_id=unit_obj.outer_build_id,
                                         unit=unit_obj.unit).count()
        unit_obj.room_num = unit_room_num if unit_room_num else 100
        unit_obj.password_num = int(15000 / project_obj.room_num * unit_obj.room_num)
        unit_obj.save()
        _set_tmp_cache_data(tmp_cache, 'unit', unit_obj,
                            outer_project_id=unit_obj.outer_project_id,
                            outer_group_id=unit_obj.outer_group_id,
                            outer_build_id=unit_obj.outer_build_id,
                            unit=unit_obj.unit)

    for room_obj in room_list:
        room_obj.project_id = project_obj.project_id
        group_obj = _get_tmp_cache_data(tmp_cache, 'group',
                                        outer_project_id=room_obj.outer_project_id,
                                        outer_group_id=room_obj.outer_group_id)
        build_obj = _get_tmp_cache_data(tmp_cache, 'build',
                                        outer_project_id=room_obj.outer_project_id,
                                        outer_group_id=room_obj.outer_group_id,
                                        outer_build_id=room_obj.outer_build_id)
        unit_obj = _get_tmp_cache_data(tmp_cache, 'unit',
                                       outer_project_id=room_obj.outer_project_id,
                                       outer_group_id=room_obj.outer_group_id,
                                       outer_build_id=room_obj.outer_build_id,
                                       unit=room_obj.unit)

        room_obj.group_id = getattr(group_obj, 'group_id', 0) or 0
        room_obj.build_id = getattr(build_obj, 'build_id', 0) or 0
        room_obj.unit_id = getattr(unit_obj, 'unit_id', 0) or 0
        room_obj.password_num = getattr(unit_obj, 'password_num', 1000) or 1000
        room_obj.save()

    name = "%sinit_project_data" % project_obj.outer_project_id
    value = pickle.dumps(unit_obj.get_project_dict())
    rc.set(name, value)


def set_xml_data(xml_name):
    def _set_collection_data(coll_dict, coll_class):
        obj = coll_class(**coll_dict)
        obj.set_qd_id()
        return obj.save_qd_obj()

    email_content, project_dict, group_dict_list, build_dict_list, unit_dict_list, room_dict_list = _get_xml_data(
        xml_name)
    if project_dict:
        check_flag, ret_obj = check_project_name_change(project_dict['outer_project_id'], project_dict['project'])
        if check_flag: update_project_name(project_dict['project'], ret_obj)

        project_obj = _set_collection_data(project_dict, Basedata_Project)
        data_list = [(group_dict_list, Basedata_Group), (build_dict_list, Basedata_Build),
                     (unit_dict_list, Basedata_Unit), (room_dict_list, Basedata_Apartment)]
        for dict_list, db_class in data_list:
            for coll in dict_list:
                _set_collection_data(coll, db_class)
        tmp_str = "%s-%s-%s同步成功" % (project_dict['province'], project_dict['city'], project_dict['project'])
        email_content = "%s\n%s" % (email_content, tmp_str) if email_content else tmp_str
        set_collection_id(project_obj)
        update_web_user_cache()
    return "%s, 文件%s" % (email_content, xml_name)


def test_get_xml_data(xml_name):
    print(set_xml_data(xml_name))


def sync_project_data(project_id):
    xml_file = '%s.xml' % project_id
    if down_xml([xml_file]):
        email_content = set_xml_data(xml_file)
        send_email(CONST['base_data_sync_email_list'], '基础数据同步', email_content)
    else:
        print("download fail")
