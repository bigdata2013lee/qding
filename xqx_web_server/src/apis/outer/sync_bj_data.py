# --*-- coding: utf8 --*--
import io
from xml.etree import ElementTree as ET

import requests

from conf.qd_conf import CONF
from models.aptm import Project, Room
from utils import tools


log = tools.get_log("django")

domain = 'www.qdingnet.com'


def _get_element_texts(parent_el, *child_el_names):

    texts = []
    for name in child_el_names:
        child = parent_el.find(name)
        text = child.text.strip() if child is not None and child.text else None
        texts.append(text)

    return texts


def down_xml(xml_file_name):
    """
    下载xml文件到指定的目录下
    :param xml_file_name:
    :return: T-#BytesIO
    """
    url = CONF.get("domain").get("www.qdingnet.com").get("apis").get("xml_download_url")
    url = "%s/%s" % (url, xml_file_name)

    log.info("down load xml: %s", url)
    session = requests.Session()

    try:
        response = session.request('get', url, timeout=20)
        temp_file = io.BytesIO(response.content)
        return temp_file

    except Exception as e:
        log.exception(e)

    return None


def get_xml_data(xml_filename):
    """

    :param xml_filename:
    :return:
    """
    xml_file = down_xml(xml_filename)
    if not xml_file:
        log.error("Down load xml file:%s fail.", xml_file)
        return

    tree = ET.parse(xml_file)
    root = tree.getroot()

    project = root.find("project")

    building_list = root.findall("./buildingList/building")
    room_list = root.findall("./roomList/room")

    email_content = ""
    if not project: email_content = "无法获得项目信息，%s" % xml_filename
    elif not building_list: email_content = "无法获得楼栋信息，%s" % xml_filename
    elif not room_list: email_content = "无法获得房屋信息，%s" % xml_filename

    if email_content:
        log.error("同步数据失败, %s" % email_content)
        return

    project_dict, project_name = get_project_data(project, xml_filename)
    if not project_dict:
        email_content = project_name
        log.error("同步数据失败, %s" % email_content)
        return

    project_obj = set_project_data(project_dict, project_name)
    if not project_obj:
        log.error("同步数据失败, 项目未建立")
        return

    set_room_data(room_list, xml_filename, project_obj, root)

    log.info("同步房间数据完成")


def _find_xml_group(xml_root, group_id):
    group_list = xml_root.findall("./communityRegionList/communityRegion")
    for group in group_list:
        _id, _name, _code = _get_element_texts(group, "id", "name", "code")
        if group_id == _id: return _name, _code

    return None, None


def _find_xml_building(xml_root, building_id):
    log.debug("building_id:%s", building_id)
    building_list = xml_root.findall("./buildingList/building")
    for building in building_list:
        _id, _name, _code, _group_id = _get_element_texts(building, "id", "name", "code", "groupId")
        log.debug("_id:%s, ", _id)
        
        if building_id == _id:
            _phase_name, _phase_code = _find_xml_group(xml_root, _group_id)

            return _code, _name, _phase_code, _phase_name

    return None, None, None, None


def get_project_data(project, xml_file):

    outer_project_id, project_name = _get_element_texts(project, "id", "name")

    if not outer_project_id: return None, "no project id %s" % xml_file
    if not project_name: return None, "project name %s" % xml_file

    return {'outer_id': outer_project_id}, project_name


def set_project_data(data, project_name):
    outer_project_id = data.get('outer_id')
    project_obj = Project.objects(source_data_info__outer_id=outer_project_id, domain=domain).first()
    if not project_obj:
        log.warning("Can not find project outer id: %s ", outer_project_id)
        return

    project_obj.name = project_name
    project_obj.domain = domain
    project_obj.saveEx()
    return project_obj


def set_room_data(room_list, xml_file, project_obj, xml_root):
    for room_el in room_list:
        build_id, = _get_element_texts(room_el, "buildingId")
        if not build_id:
            log.warning("文件%s存在找不到building_id的房屋" % xml_file)
            continue

        building_no, building_name, phase_no, phase_name = _find_xml_building(xml_root, build_id)

        log.debug("building_no:%s, building_name:%s, phase_no:%s, phase_name:%s",
                  building_no, building_name, phase_no, phase_name)

        phase_no = int(phase_no or "1")
        building_no = int(building_no or "1")

        if not phase_name: phase_name = "%d期" % phase_no
        if not building_name: building_name = "%d栋" % building_no

        room_outer_id, room_name = _get_element_texts(room_el, "id", "name")
        unit_no, floor_no, room_no = _get_element_texts(room_el, "unitCode", "floorCode", "roomCode")

        try:
            unit_no, floor_no, room_no = int(unit_no), int(floor_no), int(room_no)

        except Exception as e:
            log.warning("房间编码解析错误")
            continue

        if not room_outer_id:
            log.warning("文件%s存在无房屋id的房屋数据" % xml_file)
            continue

        _v1 = dict(phase_no=(phase_no, 100), building_no=(building_no, 1000), unit_no=(unit_no, 100),
                   floor_no=(floor_no, 100), room_no=(room_no, 100))

        _f1 = True
        for k, v in _v1.items():
            code, tv = v
            if not (1 <= code < tv):
                log.warning("错误的%s:%s, room_outer_id:%s", k, code, room_outer_id)
                _f1 = False
                break

        if not _f1: continue

        codes = [phase_no, building_no, unit_no, floor_no, room_no]
        _build_atpm(room_outer_id, project_obj, phase_name, building_name, codes)

    return True, ""


def _build_atpm(outer_id, project_obj, phase_name, building_name, codes):
    phase_no, building_no, unit_no, floor_no, room_no = codes
    aptm_uuid = tools.parse_aptm_codes_to_uuid([phase_no, building_no, unit_no, floor_no, room_no])

    data = {"outer_id": outer_id}
    room_obj = Room.objects(project=project_obj, source_data_info__outer_id=outer_id).first()

    if not room_obj: room_obj = Room(domain=domain, project=project_obj, source_data_info=data)

    room_obj.set_attrs(aptm_uuid=aptm_uuid)
    room_obj.pre_names["phase"] = phase_name
    room_obj.pre_names["building"] = building_name
    room_obj.pre_names["unit"] = "%d单元" % unit_no

    room_obj.rebuild_aptm_name()
    room_obj.saveEx()
    return room_obj
