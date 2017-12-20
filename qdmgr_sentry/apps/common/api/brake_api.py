# -*- coding:utf-8 -*-
import json
import time
import hashlib
import datetime
import traceback
import re
import pickle

from apps.brake.classes.Brake_Open_Time import Brake_Open_Time
from apps.const import CONST

from apps.brake.api.Brake_Pass_Subject import Brake_Pass_Subject
from apps.brake.api.Card_Brake_Pass_Observer import Card_Brake_Pass_Observer
from apps.brake.api.Password_Brake_Pass_Observer import Password_Brake_Pass_Observer
from apps.brake.api.Phone_Brake_Pass_Observer import Phone_Brake_Pass_Observer
from apps.basedata.classes.Basedata_Project import Basedata_Project
from apps.basedata.classes.Basedata_Group import Basedata_Group
from apps.basedata.classes.Basedata_Build import Basedata_Build
from apps.basedata.classes.Basedata_Unit import Basedata_Unit
from apps.brake.classes.Brake_Card import Brake_Card
from apps.brake.classes.Brake_Pass import Brake_Pass
from apps.common.utils.view_tools import jsonResponse
from apps.common.utils.xutil import get_key_from_dict
from apps.common.utils import qd_result, validate
from settings.const import CONST as setting_const
from apps.brake.classes.Brake_Machine import Brake_Machine
from apps.common.utils.request_api import request_bj_server
from apps.basedata.classes.Basedata_Apartment import Basedata_Apartment
from apps.brake.classes.Brake_Version import Brake_Version
from apps.sentry.classes.Sentry_Visitor import Sentry_Visitor
from apps.basedata.classes.Basedata_BJ_App_User import Basedata_BJ_App_User
from apps.brake.classes.Brake_Password import Brake_Password
from apps.web.classes.Web_User import Web_User
from apps.brake.classes.Brake_Alert import Brake_Alert
from apps.brake.classes.Brake_Config_Version import Brake_Config_Version
from apps.common.utils.sentry_date import get_time_timestamp, get_datetime_by_timestamp, get_str_day_by_datetime
from apps.brake.api.Brake_Try_Pass_Processor import Brake_Try_Pass_Processor
from apps.brake.classes.Brake_Try_Pass import Brake_Try_Pass
from apps.web.classes.Web_User import Web_User

from apps.common.utils.redis_client import rc


class Brake_Machine_Api(object):
    @jsonResponse()
    def add_brake(self, province=None, city=None, project=None, group=None, build=None, unit=None,
                  mac=None, gate_name=None, direction=None, bluetooth_rssi=None, wifi_rssi=None,
                  open_time=None):
        """
        @note: usefull: add brake
        @note: access url：/brake_api/Brake_Machine_Api/add_brake/1/
        @param province: province
        @param city: city
        @param project: project
        @param group: group
        @param build: build
        @param unit: unit
        @param mac: mac
        @param gate_name: gate name, a string of not more than 20 characters(one chinese equal one character)
        @param direction: gate direction
        @param bluetooth_rssi: bluetooth rssi
        @param wifi_rssi: wifi rssi
        @param open_time: open time
        @return: {'log': '', 'err': 0, 'msg': 'success', 'data': {'flag': 'Y'}}
        """
        try:
            result = qd_result.get_default_result()
            if not province or not city or not project:
                return qd_result.set_err_msg(result, 'province city project must exists')

            project_obj = Basedata_Project.objects(province=province, city=city, project=project).first()
            if not project_obj: return qd_result.set_err_msg(result, "project not exists")

            group_obj = None
            if group and not build and not unit:
                group_obj = Basedata_Group.objects(province=province, city=city, project=project, group=group).first()
                if not group_obj: return qd_result.set_err_msg(result, "group not exists")

            build_obj = None
            if build and not unit:
                build_obj = Basedata_Build.objects(province=province, city=city, project=project, group=group, build=build).first()
                if not build_obj: return qd_result.set_err_msg(result, "build not exists")

            unit_obj = None
            if unit:
                unit_obj = Basedata_Unit.objects(province=province, city=city, project=project, group=group,
                                                 build=build, unit=unit).first()
                if not unit_obj: return qd_result.set_err_msg(result, "unit not exists")

            bluetooth_rssi_flag, bluetooth_rssi_str = validate.validate_bluetooth_rssi(str(bluetooth_rssi))
            if not bluetooth_rssi or not bluetooth_rssi_flag: bluetooth_rssi = '-76'

            wifi_rssi_flag, wifi_rssi_str = validate.validate_wifi_rssi(str(wifi_rssi))
            if not wifi_rssi or not wifi_rssi_flag: wifi_rssi = '-76'

            open_time_flag, open_time_str = validate.validate_open_time(str(open_time))
            if not open_time or not open_time_flag: open_time = '5'

            gate_name_flag, gate_name_str = validate.validate_gate_name(gate_name)
            if not gate_name_flag: return qd_result.set_err_msg(result, gate_name_str)

            if direction not in ['I', 'O']: return qd_result.set_err_msg(result, 'direction only can be I and O')

            mac = mac.replace(":", "").replace(" ", "")
            mac_flag, mac_str = validate.validate_mac(str(mac))
            if not mac or not mac_flag: return qd_result.set_err_msg(result, mac_str)

            gate_info = {"gate_name": gate_name, "direction": direction}
            brake = Brake_Machine(gate_info=gate_info, mac=mac, bluetooth_rssi=str(bluetooth_rssi),
                                  wifi_rssi=str(wifi_rssi), open_time=str(open_time), status="1")

            brake.position = Brake_Machine.make_position(project_obj, group_obj, build_obj, unit_obj)
            brake.position_str = Brake_Machine.make_position_str(brake.position, gate_info)

            ret = brake.add_brake()
            if not ret:
                result['data']['flag'] = 'N'
                result['msg'] = '该门禁已经存在'
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def delete_brake(self, brake_id=None):
        """
        @note: 用途：删除闸机
        @note: 访问url：/brake_api/Brake_Machine_Api/delete_brake/1/
        @param brake_id: 闸机的id
        @return: {'msg': '', 'err': 0, 'log': '', 'data': {'flag': 'Y'}},Y表示删除成功，N表示删除失败
        """
        try:
            result = qd_result.get_default_result()
            brake = Brake_Machine.objects(id=brake_id).first()
            if not brake: return qd_result.set_err_msg(result, "brake_id %s not exists" % brake_id)

            brake.status = "2"
            brake.save()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def resume_brake(self, brake_id=None):
        """
        @note: 用途：删除闸机
        @note: 访问url：/brake_api/Brake_Machine_Api/resume_brake/
        @param brake_id: 闸机的id
        @return: {'msg': '', 'err': 0, 'log': '', 'data': {'flag': 'Y'}},Y表示删除成功，N表示删除失败
        """
        try:
            result = qd_result.get_default_result()
            brake = Brake_Machine.objects(id=brake_id).first()
            if brake:
                if Brake_Machine.objects(mac=brake.mac, status="1"): return qd_result.set_err_msg(result, "mac地址已存在")

                brake.status = "1"
                brake.save()
            else:
                result['data']['flag'] = 'N'
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def submit_brake(self, brake_id=None, open_time=None, bluetooth_rssi=None,
                     wifi_rssi=None, level=None, version_id=None):
        """
        @note: 用途：修改闸机信息
        @note: 访问url：/brake_api/Brake_Machine_Api/submit_brake/
        @param brake_id: brake id
        @param open_time: open time
        @param bluetooth_rssi: bluetooth rssi
        @param wifi_rssi: wifi rssi
        @param level: level
        @param version_id: version id
        @return: {'err': 0, 'data': {'flag': 'Y'}, 'msg': '修改成功', 'log': ''}
        """
        try:
            result = qd_result.get_default_result()
            open_time_flag, open_time_str = validate.validate_open_time(open_time)
            if not open_time_flag: return qd_result.set_err_msg(result, open_time_str)

            bluetooth_rssi_flag, bluetooth_rssi_str = validate.validate_bluetooth_rssi(bluetooth_rssi)
            if not bluetooth_rssi_flag: return qd_result.set_err_msg(result, bluetooth_rssi_str)

            wifi_rssi_flag, wifi_rssi_str = validate.validate_wifi_rssi(wifi_rssi)
            if not wifi_rssi_flag: return qd_result.set_err_msg(result, wifi_rssi_str)

            level_flag, level_str = validate.validate_position_level(level)
            if not level_flag: return qd_result.set_err_msg(result, level_str)

            version_obj = None
            if version_id:
                version_obj = Brake_Version.objects(id=version_id).first()
                if not version_obj: return qd_result.set_err_msg(result, 'version not exists')

            brake_obj = Brake_Machine.objects(id=brake_id).first()
            if not brake_obj: return qd_result.set_err_msg(result, "brake_id %s not exists" % brake_id)

            brake = Brake_Machine(open_time=str(open_time),
                                  bluetooth_rssi=str(bluetooth_rssi),
                                  wifi_rssi=str(wifi_rssi),
                                  level=int(level),
                                  firmware_version=version_obj.version)
            brake.modify_brake(brake_obj)

            result['msg'] = u"修改成功"
            result['data']['flag'] = 'Y'
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_brake_machine_by_filter(self, province=None, city=None, project=None, group=None,
                                    build=None, unit=None, mac=None, brake_type=None,
                                    firmware_version=None, hardware_version=None, lately_pass=None,
                                    page_no=None, page_size=None, order_field="created_time"):
        """
        @note: 用途：根据条件筛选闸机列表
        @note: 访问url：/brake_api/Brake_Machine_Api/get_brake_machine_by_filter/1/
        @param province: province
        @param city: city
        @param project: project
        @param group: group
        @param build: build
        @param unit: unit
        @param mac: mac
        @param brake_type: brake type, 1-大门, 2- 非大门
        @param page_no: 页码
        @param page_size: 每页条数
        @param firmware_version: firmware version
        @param hardware_version: hardware version
        @param lately_pass: lately pass
        @param order_field: 排序字段
        @return: {'log': '', 'msg': '', 'err': 0, 'data': {'brake_machine_list': [{'id': '564c4931c0d207a163bf74c7', 'version': {'version': '1.3'}, 'open_time': '20', 'mac': 'aa11bb22cc33', 'gate': {'gate_type': '1', 'direction': 'I', 'city': '中陲', 'province': '中陲', 'build': '3', 'gate_name': '负二楼', 'community': '千丁嘉园', 'unit': '1'}, 'bluetooth_rssi': '-80', 'wifi_rssi': '-90', 'updated_time': 1447840049821}]}}
        """
        try:
            result = qd_result.get_default_result()
            result['data']['brake_machine_list'] = []
            validate_page_flag, validate_page_str = validate.validate_pagination(page_size, page_no)
            if not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)

            brake_type_flag, brake_type_str = validate.validate_brake_type(brake_type)
            if not brake_type_flag: return qd_result.set_err_msg(result, brake_type_str)

            lately_pass_flag, lately_pass_str = validate.validate_lately_pass(lately_pass)
            if not lately_pass_flag: return qd_result.set_err_msg(result, lately_pass_str)

            brake_machine_dict_list = []
            position = {
                "position.province": province,
                "position.city": city,
                "position.project_list.project": project,
                "position.project_list.group_list.group": group,
                "position.project_list.group_list.build_list.build": build,
                "position.project_list.group_list.build_list.unit_list": unit,
            }
            reg_dict = {
                "mac": mac,
                "hardware_version": hardware_version,
                "firmware_version": firmware_version,
            }
            brake_machine_list = Brake_Machine.get_machine_by_filter(page_no, page_size, order_field, position,
                                                                     reg_dict, lately_pass, brake_type, status="1")
            if province or firmware_version or hardware_version or mac or lately_pass:
                brake_machine_dict_list = [brake_machine.get_brake_info() for brake_machine in brake_machine_list]
            result['data']['brake_machine_list'] = brake_machine_dict_list
            result['data']['brake_list'] = brake_machine_list
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': brake_machine_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_brake_machine_by_project_id_list(self, outer_project_id_list=[], page_no=1, page_size=0):
        '''
        @note: access method: /brake_api/Brake_Machine_Api/get_brake_machine_by_project_id_list/
        @param outer_project_id_list: outer project id list
        @param page_no: page no
        @param page_size: page size
        @return: {'data': {'flag': 'Y', 'pagination': {'page_size': 0, 'page_no': 1, 'total_count': 1}, 'brake_machine_list': [{'version_id': '', 'wifi_rssi': '-73', 'position': {'province': '重庆', 'city': '重庆', 'level': 5, 'project_list': [{'project': '洪泉洪逸新村', 'group_list': [{'build_list': [{'build_id': '81058', 'unit_list': ['1'], 'build': '1'}]}]}]}, 'online_status': 1, 'is_monit': 0, 'province': '重庆', 'mac': '112233445566', 'updated_time': 1468340732, 'gate_name': '网页三重门', 'id': '578519fccdc8721b16a8fe28', 'version': '', 'heart_time': 24, 'bluetooth_rssi': '-73', 'position_str': '洪泉洪逸新村1栋1单元网页三重门入', 'direction': 'I', 'city': '重庆', 'command': '0', 'open_time': '10'}]}, 'log': '', 'msg': 'success', 'err': 0}
        '''
        try:
            result = qd_result.get_default_result()

            validate_page_flag, validate_page_str = validate.validate_pagination(page_size, page_no)
            if not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)

            outer_project_id_list = json.loads(outer_project_id_list) if isinstance(outer_project_id_list,
                                                                                    str) else outer_project_id_list
            total_brake_machine_list = []
            brake_machine_list = []
            for project_id in outer_project_id_list:
                total_brake_machine_list.extend(Brake_Machine.get_project_brake(outer_project_id=str(project_id)))

            if int(page_size):
                brake_machine_list = total_brake_machine_list[(int(page_no)-1)*int(page_size):int(page_size)]

            result['data']['brake_machine_list'] = brake_machine_list
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': len(total_brake_machine_list),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_brake_info(self, brake_id=None):
        """
        @note: 用途：获取闸机信息
        @note: 访问url：/brake_api/Brake_Machine_Api/get_brake_info/
        @note: 测试demo:{brake_id:"563866ebc0d207a6931f1f5a"}
        @param brake_id: 闸机的id
        @return: {'log': '', 'data': {'province_list': ['上海', '中陲', '云南', '内蒙古', '北京', '吉林', '四川', '天津', '宁夏', '安徽', '山东', '山西', '广东', '广西', '新疆', '江苏', '江西', '河北', '河南', '浙江', '海南', '湖北', '湖南', '甘肃', '福建', '西藏', '贵州', '辽宁', '重庆', '陕西', '青海', '黑龙江'], 'city_list': ['上海'], 'build_list': ['03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62'], 'community_list': ['复瑞-象屿品城1期', '复瑞-象屿品城2期'], 'unit_list': [], 'flag': 'Y', 'brake': {'unit': '', 'status': '1', 'wifi_rssi': '', 'build': '', 'bluetooth_rssi': '', 'command': '0', 'open_time': '', 'gate': 'test', 'province': '上海', 'city': '上海', 'updated_time': 1445249327197, 'id': '5624c12fc0d2072e5be71c58', 'version': {}, 'direction': 'I', 'community': '复瑞-象屿品城1期', 'brake_type': '0'}}, 'err': 0, 'msg': ''}
        """
        try:
            result = qd_result.get_default_result()

            brake_machine = Brake_Machine.objects(id=brake_id).first()
            if not brake_machine: return qd_result.set_err_msg(result, 'retrieval brake fail')

            brake = brake_machine.get_brake_info()
            result['data']['brake'] = brake
            result['data']['brake_version_list'] = [version_obj.get_version_info() for version_obj in
                                                    Brake_Version.objects()]
            result['data']['flag'] = 'Y'
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_brake_status(self, province=None, city=None, project=None, group=None, build=None,
                         unit=None, lately_pass=None, brake_type=None, status="1", mac=None,
                         page_no=1, page_size=30, order_filed="updated_time"):
        """
        @note: 用途：获取小区闸机的在线情况
        @note: 访问url：/brake_api/Brake_Machine_Api/get_brake_status/
        @note: 测试demo:{province:"中陲","city":"中陲","community":"千丁嘉园"}
        @param province: 省份
        @param city: 城市
        @param project: 小区
        @param group: 组团
        @param build: 楼栋
        @param unit: 单元
        @param brake_type: 门禁类型
        @param lately_pass: 最近通行
        @param page_no: 页码
        @param page_size: 每页数目
        @param order_filed: 排序字段
        @param status: 状态
        @return: result:{'data': { 'flag': 'Y','online_num': 0,'offline_num': 1,'brake_list': [{'id':'dfs2123232dsf','is_monit':1,'heart_time': 12312,'status': 0, 'position': '3栋1单元负二楼-入', 'updated_time': '1444631926'}],'pagination': {'page_size': 50, 'total_count': 1, 'page_no': 1}}, 'err': 0, 'log': '', 'msg': ''}
        """
        try:
            result = qd_result.get_default_result()

            result['data'].update({
                "brake_list": [],
                "pagination": {
                    'page_no': 1,
                    'page_size': 0,
                    'total_count': 0,
                },
                "offline_num": 0,
                "online_num": 0,
            })

            validate_page_flag, validate_page_str = validate.validate_pagination(page_size, page_no)
            if not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)

            tmp_brake_list = Brake_Machine.get_machine_by_position(province=province, city=city, project=project,
                                                                   group=group, build=build, unit=unit,
                                                                   page_no=page_no, page_size=page_size,
                                                                   brake_type=brake_type, order_field=order_filed,
                                                                   lately_pass=lately_pass, status=status, mac=mac)

            project_brake_list = Brake_Machine.get_project_brake(province=province, city=city, project=project)

            for brake in project_brake_list:
                if brake['online_status_str'] == '掉线':
                    result['data']['offline_num'] += 1
                else:
                    result['data']['online_num'] += 1
            brake_list = [brake.get_brake_info() for brake in tmp_brake_list]
            if order_filed == 'status':
                brake_list = sorted(brake_list, key=lambda x: x['online_status'])
            elif order_filed == '-status':
                brake_list = sorted(brake_list, key=lambda x: -x['online_status'])
            result['data']['brake_list'] = brake_list
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': tmp_brake_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_brake_heart_time(self, brake_id=None, heart_time=None):
        """
        @note: 用途：设置闸机的心跳
        @note: 访问url：/brake_api/Brake_Machine_Api/set_brake_heart_time/
        @note: 测试demo:{brake_id:"213123213213","heart_time":"12"}
        @param brake_id: 闸机id
        @param heart_time: 心跳时间
        @return: result:{'data': {'flag': 'Y'}, 'log': '', 'msg': '', 'err': 0}
        """
        try:
            result = qd_result.get_default_result()

            heart_time_flag, heart_time_str = validate.validate_heart_time(str(heart_time))
            if not heart_time_flag: return qd_result.set_err_msg(result, heart_time_str)

            brake = Brake_Machine.objects(id=brake_id).first()
            if not brake: return qd_result.set_err_msg(result, '该闸机已经不存在')

            brake.heart_time = float(heart_time)
            brake.save()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_brake_monit(self, brake_id=None, is_monit=None):
        """
        @note: 用途：设置闸机的是否监控
        @note: 访问url：/brake_api/Brake_Machine_Api/set_brake_monit/
        @note: 测试demo:{brake_id:"213123213213","is_monit":"1"}
        @param brake_id: 闸机id
        @param is_monit: 是否监控,1-监控，0-不监控
        @return: result:{'data': {'flag': 'Y'}, 'log': '', 'msg': '', 'err': 0}
        """
        try:
            result = qd_result.get_default_result()

            if is_monit not in ['0', '1']: return qd_result.set_err_msg(result, 'is_monit只能取0,1')

            brake = Brake_Machine.objects(id=brake_id).first()
            if not brake: return qd_result.set_err_msg(result, '该闸机已经不存在')

            brake.is_monit = int(is_monit)
            brake.save()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_all_brake_machine_count(self):
        '''
        @note: usefull: get all brake machine count
        @note: access url: /brake_api/Brake_Machine_Api/get_all_brake_machine_count/
        @note: test demo: {}
        @return: {"err": 0, "msg": "", "data": {"flag": "Y", "brake_machine_count": 7425}, "log": ""}
        '''
        try:
            result = qd_result.get_default_result()
            all_brake_machine = Brake_Machine.objects(status="1")
            result['data']['brake_machine_count'] = all_brake_machine.count() if all_brake_machine else 0
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def dump_brake_machine(self, **kargs):
        try:
            result = qd_result.get_default_result()
            redis_key = get_key_from_dict(kargs)
            ret = rc.get(redis_key)
            if not ret:
                qd_result.set_err_msg(result, 'no data')
                rc.sadd("dump_data_process", pickle.dumps(kargs))
                return result
            result['data']['brake_list'] = pickle.loads(ret)
        except Exception as e:
            qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Brake_Version_Api(object):

    @jsonResponse()
    def add_brake_version(self, lowest_version=None, former_version=None, version=None, filename=None, md5sum=None,
                          message=None, project_list=[]):
        """
        @note: 用途：发布升级文件
        @note: 访问url：/brake_api/Brake_Version_Api/add_brake_version/1/
        @param lowest_version: lowest version
        @param former_version: former version, if not empty, only can be V[0-9]+.[0-9]{1,2},like V1.1, V1.1.1
        @param version: version, only can be V[0-9]+.[0-9]{1,2},like V1.1, V1.1.1
        @param filename: filename, only can be [_a-zA-Z].[a-zA-Z], like a.txt
        @params md5sum: version file md5sum, can not be empty
        @param message: version description, can empty
        @project_list: project list
        @return: {'msg': 'add version success', 'err': 0, 'data': {'flag': 'Y', 'version_id': '576cf786c0d2072c1c17a3c3'}, 'log': ''}
        """
        try:
            result = qd_result.get_default_result()
            version_flag, version_str = validate.validate_version(str(version))
            if not version_flag: return qd_result.set_err_msg(result, version_str)

            if lowest_version:
                lowest_version_flag, lowest_version_str = validate.validate_version(str(lowest_version))
                if not lowest_version_flag: return qd_result.set_err_msg(result, lowest_version_str)

            if former_version:
                former_version_flag, former_version_str = validate.validate_version(str(former_version))
                if not former_version_flag: return qd_result.set_err_msg(result, former_version_str)

            project_list = json.loads(project_list) if isinstance(project_list, str) else project_list
            if project_list:
                project_list_flag, project_list_str = validate.validate_version_project_list(project_list)
                if not project_list_flag: return qd_result.set_err_msg(result, project_list_str)

            filename_flag, filename_str = validate.validate_filename(str(filename))
            if not filename_flag: return qd_result.set_err_msg(result, filename_str)

            if not md5sum: return qd_result.set_err_msg(result, 'md5sum can not be empty')

            result["data"]["version_id"] = ""
            file_uri = "%s%s%s" % (setting_const['base']['host'], CONST['brake_relative_dir'], filename)
            brake_version = Brake_Version(lowest_version=lowest_version, former_version=former_version, version=version,
                                          file_uri=file_uri, md5sum=md5sum, message=message, project_list=project_list)
            version_obj = brake_version.add_brake_version()

            if version_obj == 1: return qd_result.set_err_msg(result, '您指定的前一个版本不存在')
            if version_obj == 2: return qd_result.set_err_msg(result, '版本已经存在')

            result["data"]["version_id"] = str(version_obj.id)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_brake_version_list(self):
        """
        @note: 用途：获取闸机版本列表
        @note: 访问url：/brake_api/Brake_Version_Api/get_brake_version_list/1/
        @return: {"data": {"version_list": [{"md5sum":"12sdfds21ssdfdsfd","file_uri": "http://sentry.qding.cloud/uploads/brake/rom/pytohn.png", "former_version": "1.0", "id": "5610c676c0d2072c909860e8", "version": "1.1"}]}, "err": 0, "msg": "", "log": ""}
        """
        try:
            result = qd_result.get_default_result()
            version_list = Brake_Version.objects(status="1")
            result['data']['version_list'] = [version.get_version_info() for version in version_list]
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def remove_version(self, version_id):
        """
        @note: 用途：删除门禁版本
        @note: 访问url：/brake_api/Brake_Version_Api/remove_version/1/
        @param version_id: brake version的id号
        @return: {'data': {'flag': 'Y'}, 'log': '', 'err': 0, 'msg': ''}
        """
        try:
            result = qd_result.get_default_result()

            brake_version = Brake_Version.objects(id=version_id).first()
            if not brake_version: return qd_result.set_err_msg(result, "version_id %s not exists" % version_id)

            brake_version.status = "2"
            brake_version.save()

        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_version(self):
        """
        @note: 用途：获取版本信息
        @note: 访问url：/brake_api/Brake_Version_Api/get_version/
        @note: 测试demo:{}
        @return: {"err": 0, "msg": "", "log": "", "data": {"config": {"id","123123213123","md5sum":"12312dsfdsfsdfds","version": "1.1", "file_uri": "http://sentry.qding.cloud/uploads/brake/rom/pytohn.png"}, "flag": "Y"}}
        """
        try:
            result = qd_result.get_default_result()
            result['data']['config'] = Brake_Version().get_newest_version()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Brake_Password_Api(object):
    """
    @note: 访客密码的相关操作
    """

    @jsonResponse()
    def add_password(self, room_id=None, app_user_id=None, valid_num=-1, reason=None, visitor_cnt=1,
                     start_time=get_time_timestamp(), end_time=get_time_timestamp(1)):
        """
        @note: 用途：添加二维码
        @note: 访问url： /brake_api/Brake_Password_Api/add_password/
        @note: 测试demo：{room_id:"6161221551685041",app_user_id:"ff8080814f1cd3d9014f9b7bf05600e9",valid_num:"-1",start_time:"1234567890",end_time:"2345678901",reason:"拜师"}
        @param room_id: 房间id
        @param app_user_id: app user id
        @param valid_num: 二维码可用次数
        @param reason: 来访原因
        @param visitor_cnt: 来访人数
        @param start_time: 密码起效时间,10位时间戳
        @param end_time: 密码失效时间，10位时间戳
        @return: {"log": "", "msg": "", "data": {"password": "928110", "flag": "Y", "visitor_id": "5636c651e3ee133f10df56ae"}, "err": 0}
        """
        try:
            result = qd_result.get_default_result()
            result["data"].update({"password": ""})
            start_time_flag, start_time_str = validate.validate_timestamp(start_time, "start_time")
            if not start_time_flag: return qd_result.set_err_msg(result, start_time_str)

            end_time_flag, end_time_str = validate.validate_timestamp(str(end_time), "end_time")
            if not end_time_flag: return qd_result.set_err_msg(result, end_time_str)

            if not reason: return qd_result.set_err_msg(result, '请填写来访原因')

            apartment = Basedata_Apartment.objects(outer_room_id=room_id).first()
            if not apartment: return qd_result.set_err_msg(result, "room_id %s 不存在" % room_id)

            password_num = apartment.password_num if apartment.password_num else 1500

            project_obj = Basedata_Project.objects(outer_project_id=apartment.outer_project_id).first()
            if not project_obj: return qd_result.set_err_msg(result, "楼盘数据不存在")

            project_unit_count = project_obj.unit_num if project_obj.unit_num else 30

            brake_machine_list = Brake_Machine.get_project_brake(outer_project_id=apartment.outer_project_id)
            if not brake_machine_list: return qd_result.set_err_msg(result, "该小区未安装门禁")

            brake_version = brake_machine_list[0]['version']

            bj_app_user, ret_str = Basedata_BJ_App_User(
                outer_app_user_id=app_user_id).get_app_user_by_outer_app_user_id()
            if not bj_app_user: return qd_result.set_err_msg(result, ret_str)

            _start_time = datetime.datetime.fromtimestamp(int(start_time))
            _end_time = datetime.datetime.fromtimestamp(int(end_time))
            visitor_password = Brake_Password()
            visitor_password.password_type = "1"
            visitor_password.valid_num = int(valid_num)
            visitor_password.coming = "0"
            visitor_password.start_time = _start_time
            visitor_password.end_time = _end_time
            visitor_password.bj_app_user = bj_app_user
            visitor_password.apartment = apartment
            visitor_password.apartment_dict = apartment.get_apartment_info()

            visitor = Sentry_Visitor()
            visitor.visitor_type = "1"
            visitor.name = "APP"
            visitor.reason = reason
            visitor.coming = "0"
            visitor.visitor_cnt = visitor_cnt
            visitor.start_time = _start_time
            visitor.end_time = _end_time
            visitor_password.add_password(project_unit_count, brake_version, visitor, password_num)
            if not visitor_password.password: return qd_result.set_err_msg(result, '生成密码失败')

            value = pickle.dumps({
                "member_id": bj_app_user.outer_member_id,
                "pwd": visitor_password.password,
                "valid_num": visitor_password.valid_num,
                "room_id": room_id,
                "start_time": start_time,
                "end_time": end_time,
            })
            rc.rpush("send_password_to_cloud_talker", value)

            visitor.brake_password = visitor_password
            visitor.set__brake_password()
            visitor.save()
            result['data']['password'] = visitor_password.password
            result['data']['flag'] = 'Y'
            result['data']['visitor_id'] = visitor.id
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Brake_Pass_Api(object):
    """
    @note: 用户通行接口类
    """

    @jsonResponse()
    def set_user_pass_list(self, user_pass_list=[]):
        """
        @note: 用途：批量上报通行记录
        @note: 访问url： /brake_api/Brake_Pass_Api/set_user_pass_list/
        @note: 蓝牙记录demo:{user_pass_list:'[{"created_time":"1444631626","mac":"2233abxs4676","pass_type":"0","app_user_id":"20160229(app_user_id)"}]'}
        @note: wifi记录demo:{user_pass_list:'[{"created_time":"1444631626","mac":"2233abxs4676","pass_type":"1","app_user_id":"20160229(app_user_id)"}]'}
        @note: 密码记录demo:{user_pass_list:'[{"created_time":"1444631626","mac":"2233abxs4676","pass_type":"2","app_user_id":"123456(password)"}]'}
        @note: 卡记录demo:{user_pass_list:'[{"created_time":"1444631626","mac":"2233abxs4676","pass_type":"4","app_user_id":"123123(card_no)"}]'}
        @param user_pass_list: 通行记录列表, 长度限制为1-100条记录
        @return: {'err': 0, 'msg': '', 'log': '', 'data': {'flag': 'Y','user_pass_list_length':1}}
        """
        try:
            result = qd_result.get_default_result()
            user_pass_list = json.loads(user_pass_list) if isinstance(user_pass_list, str) else user_pass_list
            for user_pass in user_pass_list:
                user_pass = json.dumps(user_pass, sort_keys=True)
                r_flag = rc.sadd('user_pass_set', user_pass)
                if r_flag is False: return qd_result.set_err_msg(result, 'the length of list is great than 5000')
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_user_try_pass_list(self, user_try_pass_list=[]):
        '''
        @note: 用途: 批量上传用户尝试开门记录
        @note: 访问url： /brake_api/Brake_Pass_Api/set_user_try_pass_list/
        @param user_try_pass_list: user try pass list
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            user_try_pass_list = json.loads(user_try_pass_list) if isinstance(user_try_pass_list, str) else user_try_pass_list
            for user_try_pass in user_try_pass_list:
                user_try_pass = json.dumps(user_try_pass, sort_keys=True)
                r_flag = rc.sadd('user_try_pass_set', user_try_pass)
                if r_flag is False: return qd_result.set_err_msg(result, 'the length of list is great than 5000')
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_user_pass(self, created_time=None, mac=None, pass_type=None, app_user_id=None, server_id=None):
        """
        @note: access url： /brake_api/Brake_Pass_Api/set_user_pass/
        @note: test demo:{"created_time":"1444631626","app_user_id":"ff8080814d7a5e08014d7ab0daf4001c","mac":"2233abxs4676","pass_type":"0"}
        @param created_time: created time
        @param app_user_id: app user id
        @param server_id: password or other id
        @param mac: mac
        @param pass_type: 0-bluetooth，1-wifi，2-password, 3-card
        @return: {'err': 0, 'msg': '', 'log': '', 'data': {'flag': 'Y'}}
        """
        try:
            result = qd_result.get_default_result()
            tmp_created_time = datetime.datetime.fromtimestamp(int(created_time))
            bp = Brake_Pass(pass_type=pass_type, created_time=tmp_created_time)
            bps = Brake_Pass_Subject()

            sentry_visitor = None

            brake_obj = Brake_Machine.get_brake_by_mac(mac=mac)
            if not brake_obj: return qd_result.set_err_msg(result, "mac %s not exits" % mac)

            brake_machine = Brake_Machine.get_brake_info_for_pass(brake_obj=brake_obj)

            outer_project_id = brake_machine['position']['project_list'][0]['outer_project_id']

            validate_num_flag, validate_num_str = validate.validate_num(str(app_user_id), "app_user_id")
            if validate_num_flag: app_user_id = int(app_user_id) # 兼容app_user_id 和 outer_app_user_id两种方案

            if pass_type in ['0', '1']:
                pass_media = Basedata_BJ_App_User.get_app_for_pass(app_user_id=app_user_id)
                if not pass_media: return qd_result.set_err_msg(result, "app_user_id %s not exists" % app_user_id)

                Phone_Brake_Pass_Observer(bps)
            elif pass_type == '2':
                if not server_id: server_id = app_user_id
                server_id, server_id_str = validate.validate_server_id(server_id)
                if not server_id: return qd_result.set_err_msg(result, server_id_str)

                str_day = get_str_day_by_datetime(tmp_created_time, "%Y%m%d")
                pass_media = Brake_Password.get_password(str_day, outer_project_id, server_id)
                if not pass_media: return qd_result.set_err_msg(result, "password %s not exists" % server_id)

                sentry_visitor = Sentry_Visitor.objects(brake_password=pass_media).first()
                if not sentry_visitor: return qd_result.set_err_msg(result, "no sentry_visitor %s" % server_id)

                Password_Brake_Pass_Observer(bps, sentry_visitor)
            elif pass_type == '4':
                rpp = "%s-%s" % (brake_machine['position_str'], mac)
                pass_media = Brake_Card.get_card_info_for_brake_pass(enc_card_no=app_user_id, rpp=rpp)
                Card_Brake_Pass_Observer(bps)
            else:
                return qd_result.set_err_msg(result, "illegal pass_type %s" % pass_type)

            set_flag, set_str = bps.set_pass_data(brake_machine, pass_media, bp)
            if not set_flag: return qd_result.set_err_msg(result, set_str)

            apartment = Basedata_Apartment()
            bp.set_pass(result, apartment, brake_obj, sentry_visitor)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_user_try_pass(self,  created_time=None, mac=None, pass_type=None, app_user_id=None, pass_mode=None, pass_code=None):
        """
        @note: access url： /brake_api/Brake_Pass_Api/set_user_pass/
        @note: test demo:{"created_time":"1444631626",""mac":"2233abxs4676","pass_type":"0",app_user_id":"1290111881","pass_mode":"100","code":"1005","pass_time":"1444631626000"}
        @param created_time: 通行时间
        @param mac: 门禁设备MAC地址
        @param pass_type: 通行方式：0-bluetooth, 1-WiFi，2-password，4-card, 5-exit button， 6-hal warning 9-password failed 10-card failed 11-config
        @param app_user_id:当pass_type等于0,1时，app_user_id为手机用户ID；当pass_type等于2,9时，app_user_id为访客密码；当pass_type等于4,10时，app_user_id为门禁卡号；当pass_type等于11时，app_user_id为手机号码
        @param pass_mode: 通行模式：#100-手动, 101-自动
        @param pass_code: 通行结果代码
        @param pass_request_time: 手机APP请求通行开始时间
        @return: {'err': 0, 'msg': '', 'log': '', 'data': {'flag': 'Y'}}
        """
        try:
            result = qd_result.get_default_result()
            tmp_created_time = None
            if created_time:
                tmp_created_time = datetime.datetime.fromtimestamp(int(created_time))

            btp = Brake_Try_Pass(pass_type=pass_type, created_time=tmp_created_time)

            pass_user = None
            pass_medium = None
            sentry_visitor = None

            validate_pass_mode_flag, validate_pass_mode_str = validate.validate_num(str(pass_mode), "pass_mode")
            if not validate_pass_mode_flag: return qd_result.set_err_msg(result, validate_pass_mode_str)

            validate_code_flag, validate_code_str = validate.validate_num(str(pass_code), "pass_code")
            if not validate_code_flag: return qd_result.set_err_msg(result, validate_code_str)

            pass_info = {
                'pass_mode': pass_mode,
                'pass_code': pass_code,
            }

            brake_machine = Brake_Machine.get_brake_by_mac(mac=mac)
            if not brake_machine: return qd_result.set_err_msg(result, "mac %s not exits" % mac)
            pass_device = Brake_Machine.get_brake_info_for_pass(brake_machine)
            outer_project_id = pass_device['position']['project_list'][0]['outer_project_id']

            if pass_type in ['0', '1']:
                validate_num_flag, validate_num_str = validate.validate_num(str(app_user_id), "app_user_id")
                if validate_num_flag: app_user_id = int(app_user_id)  # 兼容app_user_id 和 outer_app_user_id两种方案

                pass_user = Basedata_BJ_App_User.get_app_for_pass(app_user_id=app_user_id)
                if not pass_user:
                    return qd_result.set_err_msg(result, "app_user_id %s not exists" % app_user_id)
            elif pass_type in ['2', '9']:
                server_id = app_user_id
                server_id, server_id_str = validate.validate_server_id(server_id=server_id)
                if not server_id: return qd_result.set_err_msg(result, server_id_str)

                str_day = get_str_day_by_datetime(tmp_created_time, "%Y%m%d")
                pass_medium = Brake_Password.get_password(str_day, outer_project_id, server_id)
                if not pass_medium: return qd_result.set_err_msg(result, "password %s not exists" % server_id)

                sentry_visitor = Sentry_Visitor.objects(brake_password=pass_medium).first()
                if not sentry_visitor: return qd_result.set_err_msg(result, "no sentry_visitor %s" % server_id)

                if pass_type == '2':
                    pass_info.update({'pass_code': 0})
                elif pass_type == '9':
                    pass_info.update({'pass_code': 1})
            elif pass_type in ['4', '10']:
                enc_card_no = app_user_id
                validate_card_no_flag, validate_card_no_str = validate.validate_enc_card_no(enc_card_no=enc_card_no)
                if not validate_card_no_flag: return qd_result.set_err_msg(result, validate_card_no_str)

                rpp = "%s-%s" % (brake_machine['position_str'], mac)
                pass_medium = Brake_Card.get_card_info_for_brake_pass(enc_card_no=enc_card_no, rpp=rpp)
                if not pass_medium: return qd_result.set_err_msg(result, "brake card %s not exists" % app_user_id)
            elif pass_type == '11':
                validate_num_flag, validate_num_str = validate.validate_num(str(app_user_id), "app_user_id")
                if not validate_num_flag: return qd_result.set_err_msg(result, validate_num_str)

                phone = Brake_Try_Pass.get_phone_from_app_user_id(app_user_id)
                pass_user = Web_User.get_web_user_by_phone(phone)
                if not pass_user: return qd_result.set_err_msg(result, "configer user %s not exists" % phone)
            elif pass_type in ['5', '6', '7']:
                validate_num_flag, validate_num_str = validate.validate_num(str(app_user_id), "app_user_id")
                if not validate_num_flag: return qd_result.set_err_msg(result, validate_num_str)
                pass_user = {
                    'app_user_id': int(app_user_id),
                }
            else:
                return qd_result.set_err_msg(result, "illegal pass_type %s" % pass_type)

            btpp = Brake_Try_Pass_Processor(pass_user=pass_user,
                                            pass_device=pass_device,
                                            pass_medium=pass_medium,
                                            pass_info=pass_info,
                                            sentry_visitor=sentry_visitor)

            set_flag, set_str = btpp.set_pass_data(brake_try_pass=btp)
            if not set_flag: return qd_result.set_err_msg(result, set_str)

            btp.save_data(brake_machine, sentry_visitor, result)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_pass_list_by_position(self, province=None, city=None, project=None, group=None, build=None,
                                  unit=None, page_size='30', page_no='1', pass_type="", brake_type=None,
                                  start_time=None, end_time=None):
        """
        @note: 用途：获取小区用户的闸机通行记录
        @note: 访问url： /brake_api/Brake_Pass_Api/get_pass_list_by_position/1/
        @note: 测试demo: {province:"重庆",city:"重庆",project:"江与城南区", group:"二组团", build:"33", unit:"1"}
        @param province: 省份
        @param city: 城市
        @param project: 小区
        @param page_size: 每页的数目
        @param page_no: 具体哪一页  
        @param pass_type: 通行类型，0-蓝牙,1-wifi，2-密码， 4-卡
        @param brake_type: 门禁类型, 2-大门, 3-非大门
        @param start_time: 开始时间,10位时间戳
        @param end_time: 结束时间,10位的时间戳
        @return: {'err': 0, 'msg': '', 'log': '', 'data': {'flag':'Y','url':'','pass_list':[],'pagination':{'page_no':1,'page_size':50,'total_count':100}}}
        """
        try:
            result = qd_result.get_default_result()
            validate_page_flag, validate_page_str = validate.validate_pagination(page_size, page_no)
            if not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)
            start_time_flag, start_time_str = validate.validate_timestamp(str(start_time), "start_time")
            end_time_flag, end_time_str = validate.validate_timestamp(str(end_time), "end_time")
            if start_time and end_time and not (start_time_flag or end_time_flag):
                msg = start_time_str, end_time_str
                return qd_result.set_err_msg(result, msg)
            if pass_type not in ['0', '1', '2', '4']:
                pass_type = None
            if brake_type not in ['2', '3']:
                brake_type = None
            else:
                brake_type = int(brake_type)
            brake_pass = Brake_Pass()
            brake_pass_list = brake_pass.get_brake_pass_list_by_position(province=province, city=city, project=project,
                                                                         group=group, build=build, unit=unit,
                                                                         brake_type=brake_type, pass_type=pass_type,
                                                                         page_size=int(page_size), page_no=int(page_no),
                                                                         start_time=start_time, end_time=end_time)
            if not brake_pass_list:
                total_count = 0
            else:
                total_count = brake_pass_list.count()
            result['data']['pass_list'] = [brake_pass.get_brake_pass_info() for brake_pass in brake_pass_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': total_count,
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_community_day_pass_count(self, province=None, city=None, community=None,
                                     start_day=int(time.time()) - 30 * 24 * 3600,
                                     end_day=int(time.time())):
        '''
        @note: use:get community total pass of every day by brake
        @note: access url:/brake_api/Brake_Pass_Api/get_community_day_pass_count/
        @note: test demo:{province:"",city:"",community:"",start_day:"1234567890",end_day:"1234567890"}
        @param province: province
        @param city: city
        @param community: community
        @param start_day: start day
        @param end_day: end day
        @return: result:{'err': 0, 'msg': '', 'log': '', 'data': {'day_pass_count_list': [{'unit_gate_pass_num': 0, 'day': '2015-11-03', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-04', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-05', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-06', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-07', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-08', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-09', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-10', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-11', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-12', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-13', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-14', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-15', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-16', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-17', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-18', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-19', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-20', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-21', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-22', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-23', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-24', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 1, 'day': '2015-11-25', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-26', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-27', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-28', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-29', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-11-30', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-12-01', 'cummunity_gate_pass_num': 0}, {'unit_gate_pass_num': 0, 'day': '2015-12-02', 'cummunity_gate_pass_num': 0}]}}
        '''
        try:
            result = qd_result.get_default_result()
            start_day_flag, start_day_str = validate.validate_timestamp(str(start_day), "start_day")
            if not start_day_flag: return qd_result.set_err_msg(result, start_day_str)

            end_day_flag, end_day_str = validate.validate_timestamp(str(end_day), "end_day")
            if not end_day_flag: return qd_result.set_err_msg(result, end_day_str)

            if not province or not city or not community: return qd_result.set_err_msg(result,
                                                                                       'no have province or no have city or no have community')
            brake_pass = Brake_Pass()
            day_pass_count_list = brake_pass.get_project_day_pass_count(province, city, community, int(start_day),
                                                                        int(end_day))
            result['data']['day_pass_count_list'] = day_pass_count_list
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_all_pass_count(self):
        '''
        @note: usefull:get all pass count
        @note: access url:/brake_api/Brake_Pass_Api/get_all_pass_count/
        @note: test demo: {}
        @return: {"log": "", "msg": "", "err": 0, "data": {"flag": "Y", "pass_count": 506348}}
        '''
        try:
            result = qd_result.get_default_result()
            old_pass_count = Brake_Pass().get_all_pass().count()
            try_pass_count = Brake_Try_Pass.get_all_pass_count()
            result['data']['pass_count'] = old_pass_count + try_pass_count
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_user_pass_list(self, app_user_id, page_size='50', page_no='1'):
        """
        @note: 用途：获取用户的通行记录
        @note: 访问url： /brake_api/Brake_Pass_Api/get_user_pass_list/
        @note: 测试demo: {outer_app_user_id:"ff8080814fc9c65e014fc9d39a7e0003",page_size:"50",page_no:"1"}
        @param app_user_id: app用户id
        @param page_size: 每页的数目
        @param page_no: 具体哪一页
        @return: {"err": 0, "msg": "", "log": "", "data": {"user_pass_list": [{"created_time": 1444633636, "position": "观山水testtt"}]}}
        """
        try:
            result = qd_result.get_default_result()
            user_pass_list = Brake_Pass().get_brake_pass_list_by_outer_app_user_id(outer_app_user_id=app_user_id,
                                                                                   page_no=int(page_no),
                                                                                   page_size=int(page_size))
            result['data']['user_pass_list'] = [user_pass.get_brake_pass_info() for user_pass in user_pass_list]
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_user_pass_list_by_phone(self, phone, page_size=30, page_no=1, sorted_field='-updated_time'):
        '''
        @note: usefull:get user pass list
        @note: access url:/brake_api/Brake_Pass_Api/get_user_pass_list_by_phone/1/
        @param phone: phone
        @param page_size:page size
        @param page_no: page number
        @param sorted_field: updated time
        @return: {'data': {'pagination': {'page_size': 30, 'total_count': 3, 'page_no': 1}, 'user_pass_list': [{'community': '洪泉洪逸新村', 'city': '重庆', 'created_time': 1461815394, 'room': '1栋1单元物业办公室', 'type': '0', 'direction': 'I', 'phone': '12345678901', 'position': '洪泉洪逸新村1栋1单元配置工具三重门入'}], 'flag': 'Y'}, 'msg': 'success', 'log': '', 'err': 0}
        '''
        try:
            result = qd_result.get_default_result()
            result['data']['user_pass_list'] = []
            validate_page_flag, validate_page_str = validate.validate_pagination(str(page_size), str(page_no))
            if page_size and page_no and not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)
            brake_pass_list = Brake_Pass.get_brake_pass_list_by_phone(phone=phone, page_no=int(page_no),
                                                                      page_size=int(page_size),
                                                                      sorted_field=sorted_field)
            result['data']['user_pass_list'] = [brake_pass.get_brake_pass_info() for brake_pass in brake_pass_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': brake_pass_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_brake_pass_list(self, mac, page_no=1, page_size=30):
        '''
        @note: usefull: get brake pass list
        @note: access url:/brake_api/Brake_Pass_Api/get_brake_pass_list/1/
        @note: test demo:{mac:"12312321323123"}
        @param mac:mac
        @param page_no: page number
        @param page_size: page size
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            result['data']['brake_pass_list'] = []
            validate_page_flag, validate_page_str = validate.validate_pagination(str(page_size), str(page_no))
            if not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)
            brake_pass_list = Brake_Pass. \
                get_brake_pass_list_by_mac(mac=mac, page_no=int(page_no), page_size=int(page_size))
            result['data']['brake_pass_list'] = [brake_pass.get_brake_pass_info() for brake_pass in brake_pass_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': brake_pass_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_user_pass_list_by_card(self, card_no, page_no=1, page_size=30):
        '''
        @note: usefull 获取门禁卡的通行记录
        @note: access url: /brake_api/Brake_Pass_Api/get_user_pass_list_by_card/
        :param card_no: card no
        :param page_no: page no
        :param page_size: page size
        :return:
        '''
        try:
            result = qd_result.get_default_result()
            result['data']['brake_pass_list'] = []
            validate_page_flag, validate_page_str = validate.validate_pagination(str(page_size), str(page_no))
            if not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)

            brake_pass_list = Brake_Pass. \
                get_brake_pass_list_by_card_no(card_no=int(card_no), page_no=int(page_no), page_size=int(page_size))
            result['data']['brake_pass_list'] = [brake_pass.get_brake_pass_info() for brake_pass in brake_pass_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': brake_pass_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_brake_pass_by_project_id_list(self, outer_project_id_list=[], start_time=int(time.time()) - 30 * 24 * 3600,
                                     end_time=int(time.time())):
        '''
        @note: 根据社区ID列表获取通行记录数据
        @note: 访问url： /brake_api/Brake_Pass_Api/get_brake_pass_by_project_id_list/1/
        @note: 测试demo:
        :param outer_project_id_list:社区ID列表
        :param start_day:开始日期
        :param end_day:结束日期
        :return:
        '''

        try:
            result = qd_result.get_default_result()

            start_day_flag, start_day_str = validate.validate_timestamp(str(start_time), 'start_time')
            if not start_day_flag: return qd_result.set_err_msg(result, start_day_str)

            end_day_flag, end_day_str = validate.validate_timestamp(str(end_time), 'end_time')
            if not end_day_flag: return qd_result.set_err_msg(result, end_day_str)

            outer_project_id_list = json.loads(outer_project_id_list) if isinstance(outer_project_id_list,
                                                                                    str) else outer_project_id_list

            start_day = get_datetime_by_timestamp(int(start_time))
            end_day = get_datetime_by_timestamp(int(end_time), index=1)

            raw_query = {
                'pass_info.brake_machine.position.project_list.outer_project_id': {
                    "$in": outer_project_id_list
                },
                'status': '1',
                'created_time': {"$gt": start_day, "$lt": end_day}
            }
            brake_pass_list = Brake_Pass.objects(__raw__=raw_query).\
                order_by('pass_info.brake_machine.position.project_list.outer_project_id')

            result['data']['brake_pass_list'] = [brake_pass.get_brake_pass_info() for brake_pass in brake_pass_list]
            result['data']['pagination'] = {
                'total_count': brake_pass_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_try_pass_list_by_position(self, province=None, city=None, project=None, group=None, build=None,
                                  unit=None, page_size='30', page_no='1', pass_type="", brake_type=None,
                                  start_time=None, end_time=None):
        """
        @note: 用途：获取小区用户的闸机通行记录
        @note: 访问url： /brake_api/Brake_Pass_Api/get_try_pass_list_by_position/1/
        @note: 测试demo: {province:"重庆",city:"重庆",project:"江与城南区", group:"二组团", build:"33", unit:"1"}
        @param province: 省份
        @param city: 城市
        @param project: 小区
        @param page_size: 每页的数目
        @param page_no: 具体哪一页
        @param pass_type: 通行类型，0-蓝牙,1-wifi，2-密码， 4-卡
        @param brake_type: 门禁类型, 2-大门, 3-非大门
        @param start_time: 开始时间,10位时间戳
        @param end_time: 结束时间,10位的时间戳
        @return: {'err': 0, 'msg': '', 'log': '', 'data': {'flag':'Y','url':'','pass_list':[],'pagination':{'page_no':1,'page_size':50,'total_count':100}}}
        """
        try:
            result = qd_result.get_default_result()
            validate_page_flag, validate_page_str = validate.validate_pagination(page_size, page_no)
            if not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)
            start_time_flag, start_time_str = validate.validate_timestamp(str(start_time), "start_time")
            end_time_flag, end_time_str = validate.validate_timestamp(str(end_time), "end_time")
            if start_time and end_time and not (start_time_flag or end_time_flag):
                msg = start_time_str, end_time_str
                return qd_result.set_err_msg(result, msg)
            if pass_type not in ['0', '1', '2', '4', '6', '11']:
                pass_type = None
            if brake_type not in ['2', '3']:
                brake_type = None
            else:
                brake_type = int(brake_type)

            brake_try_pass_list = Brake_Try_Pass.get_brake_try_pass_list_by_position(province=province, city=city, project=project,
                                                                         group=group, build=build, unit=unit,
                                                                         brake_type=brake_type, pass_type=pass_type,
                                                                         page_size=int(page_size), page_no=int(page_no),
                                                                         start_time=start_time, end_time=end_time)
            if not brake_try_pass_list:
                total_count = 0
            else:
                total_count = brake_try_pass_list.count()
            result['data']['pass_list'] = [brake_pass.get_brake_try_pass_info() for brake_pass in brake_try_pass_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': total_count,
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_user_try_pass_list_by_phone(self, phone, page_size=30, page_no=1, sorted_field='-updated_time'):
        '''
        @note: usefull:get user pass list
        @note: access url:/brake_api/Brake_Pass_Api/get_user_try_pass_list_by_phone/1/
        @param phone: phone
        @param page_size:page size
        @param page_no: page number
        @param sorted_field: updated time
        @return: {'data': {'pagination': {'page_size': 30, 'total_count': 3, 'page_no': 1}, 'user_pass_list': [{'community': '洪泉洪逸新村', 'city': '重庆', 'created_time': 1461815394, 'room': '1栋1单元物业办公室', 'type': '0', 'direction': 'I', 'phone': '12345678901', 'position': '洪泉洪逸新村1栋1单元配置工具三重门入'}], 'flag': 'Y'}, 'msg': 'success', 'log': '', 'err': 0}
        '''
        try:
            result = qd_result.get_default_result()
            result['data']['user_pass_list'] = []
            validate_page_flag, validate_page_str = validate.validate_pagination(str(page_size), str(page_no))
            if page_size and page_no and not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)
            brake_try_pass_list = Brake_Try_Pass.get_brake_try_pass_list_by_phone(phone=phone, page_no=int(page_no),
                                                                      page_size=int(page_size),
                                                                      sorted_field=sorted_field)
            result['data']['user_pass_list'] = [brake_pass.get_brake_try_pass_info() for brake_pass in brake_try_pass_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': brake_try_pass_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_user_try_pass_list_by_card(self, card_no, page_no=1, page_size=30):
        '''
        @note: usefull 获取门禁卡的通行记录
        @note: access url: /brake_api/Brake_Pass_Api/get_user_try_pass_list_by_card/
        :param card_no: card no
        :param page_no: page no
        :param page_size: page size
        :return:
        '''
        try:
            result = qd_result.get_default_result()
            result['data']['brake_pass_list'] = []
            validate_page_flag, validate_page_str = validate.validate_pagination(str(page_size), str(page_no))
            if not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)

            brake_try_pass_list = Brake_Try_Pass. \
                get_brake_try_pass_list_by_card_no(card_no=int(card_no), page_no=int(page_no), page_size=int(page_size))
            result['data']['brake_pass_list'] = [brake_pass.get_brake_try_pass_info() for brake_pass in brake_try_pass_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': brake_try_pass_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_failed_user_try_pass_list(self, province=None, city=None, project=None, group=None, build=None,
                                  unit=None, mac=None, pass_type="", phone=None,  start_time=None,
                                  end_time=None, page_size='30', page_no='1'):
        """
        @note: 用途：获取通行失败日志
        @note: 访问url： /brake_api/Brake_Pass_Api/get_failed_user_try_pass_list/1/
        @note: 测试demo: {province:"重庆",city:"重庆",project:"江与城南区", group:"二组团", build:"33", unit:"1", mac:"883B8B038325", pass_type:"9", phone:"13426349176", start_time:"1501545600", end_time:"1502841600"}
        @param province: 省份
        @param city: 城市
        @param project: 小区
        @param group: 组团
        @param build: 楼栋
        @param unit: 单元
        @param mac: 门禁设备MAC地址
        @param pass_type: 通行类型，0-蓝牙，1-WIFI，9-密码， 10-卡
        @param phone: 当pass_type=0,1,9：手机号；当pass_type=10：卡号；
        @param start_time: 开始时间,10位时间戳
        @param end_time: 结束时间,10位的时间戳
        @paam page_size: 每页的数目
        @param page_no: 具体哪一页
        @return: {'err': 0, 'msg': '', 'log': '', 'data': {'flag':'Y','url':'','pass_list':[],'pagination':{'page_no':1,'page_size':50,'total_count':100}}}
        """
        try:
            result = qd_result.get_default_result()
            validate_page_flag, validate_page_str = validate.validate_pagination(page_size, page_no)
            if not validate_page_flag: return qd_result.set_err_msg(result, validate_page_str)
            start_time_flag, start_time_str = validate.validate_timestamp(str(start_time), "start_time")
            end_time_flag, end_time_str = validate.validate_timestamp(str(end_time), "end_time")
            if start_time and end_time and not (start_time_flag or end_time_flag):
                msg = start_time_str, end_time_str
                return qd_result.set_err_msg(result, msg)
            if pass_type not in ['0', '1', '9', '10']:
                pass_type = None

            failed_pass_list = Brake_Try_Pass.get_failed_brake_try_pass_list(province=province, city=city,
                                                                            project=project,
                                                                            group=group, build=build,
                                                                            unit=unit, mac=mac,
                                                                            pass_type=pass_type,
                                                                            phone=phone,
                                                                            page_size=int(page_size),
                                                                            page_no=int(page_no),
                                                                            start_time=start_time,
                                                                            end_time=end_time)
            if not failed_pass_list:
                total_count = 0
            else:
                total_count = failed_pass_list.count()
            result['data']['pass_list'] = [brake_pass.get_brake_try_pass_info() for brake_pass in failed_pass_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': total_count,
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

class Brake_Alert_Api(object):
    """
    @note: 报警设置操作类
    """

    @jsonResponse()
    def add_alerter(self, web_user_id=None, alert_email=None):
        """
        @note: 用途：报警设置,修改报警邮件
        @note: 访问url： /brake_api/Brake_Alert_Api/add_alerter/1/
        @note: 测试demo:{web_user_id:'fdssd121232',alert_email:'12323@163.com'}
        @param web_user_id: web用户的id
        @param alert_email: 报警邮箱
        @return: result:{'log': '', 'data': {'flag': 'Y'}, 'msg': '', 'err': 0}
        """
        try:
            result = qd_result.get_default_result()
            result["data"].update({"alert_id": ""})
            web_user_id_flag, web_user_id_str = validate.validate_mongodb_id(web_user_id)
            if not web_user_id_flag: return qd_result.set_err_msg(result, web_user_id_str)

            web_user = Web_User(id=web_user_id).get_user_by_id()
            if not web_user: return qd_result.set_err_msg(result, 'web用户已经不存在')

            brake_alert = Brake_Alert(web_user=web_user, alert_email=alert_email)
            tmp_brake_alert = brake_alert.get_alert_by_filter()
            if tmp_brake_alert:
                return qd_result.set_err_msg(result, '该邮箱已经存在')
            else:
                brake_alert = brake_alert.save()
                result['data']['alert_id'] = str(brake_alert.id)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_alerter(self, alert_id=None, alert_email=None):
        """
        @note: 用途：报警设置,修改报警邮件
        @note: 访问url： /brake_api/Brake_Alert_Api/set_alerter/1/
        @note: 测试demo:{alert_id:'fdssd121232',alert_email:'12323@163.com'}
        @param alert_id: 报警邮箱id
        @param alert_email: 报警邮箱
        @return: result:{'log': '', 'data': {'flag': 'Y'}, 'msg': '', 'err': 0}
        """
        try:
            result = qd_result.get_default_result()
            alert_id_flag, alert_id_str = validate.validate_mongodb_id(alert_id)
            if not alert_id_flag: return qd_result.set_err_msg(result, alert_id_str)
            email_flag, email_str = validate.validate_email(str(alert_email))
            if not email_flag: return qd_result.set_err_msg(result, email_str)
            brake_alert = Brake_Alert(id=alert_id).get_alert_by_id()
            if not brake_alert: return qd_result.set_err_msg(result, '该邮箱不存在')
            brake_alert.alert_email = alert_email
            tmp_brake_alert = Brake_Alert(web_user=brake_alert.web_user, alert_email=brake_alert.alert_email)
            if tmp_brake_alert.get_alert_by_filter().first(): return qd_result.set_err_msg(result, '该email已被占用，请勿重复设置')
            brake_alert.save()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_alerter(self, web_user_id=None):
        """
        @note: 用途：报警设置
        @note: 访问url： /brake_api/Brake_Alert_Api/get_alerter/1/
        @note: 测试demo:{web_user_id:'sdfds213123'}
        @param web_user_id: web用户的id
        @return: result:{'msg': '', 'err': 0, 'data': {'brake_alert_list': [{'alert_email': 'sfsdf@dsd.cn', 'id': '56594ebec0d2079b88f04123'}], 'flag': 'Y'}, 'log': ''}
        """
        try:
            result = qd_result.get_default_result()
            result['data'].update({'brake_alert_list': []})
            web_user_id_flag, web_user_id_str = validate.validate_mongodb_id(web_user_id)
            if not web_user_id_flag: return qd_result.set_err_msg(result, web_user_id_str)
            web_user = Web_User(id=web_user_id).get_user_by_id()
            if not web_user: return qd_result.set_err_msg(result, 'web用户已经不存在')
            brake_alert = Brake_Alert(web_user=web_user)
            brake_alert_list = brake_alert.get_alert_by_user()
            result['data']['brake_alert_list'] = [brake_alert.get_alert_info() for brake_alert in brake_alert_list]
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def delete_alerter(self, alert_id=None):
        """
        @note: 用途：删除报警邮件
        @note: 访问url： /brake_api/Brake_Alert_Api/delete_alerter/1/
        @note: 测试demo:{alert_id:'fdssd121232'}
        @param alert_id: 报警邮箱id
        @return: {'err': 0, 'msg': '', 'log': '', 'data': {'flag': 'Y'}}
        """
        try:
            result = qd_result.get_default_result()
            alert_id_flag, alert_id_str = validate.validate_mongodb_id(alert_id)
            if not alert_id_flag: return qd_result.set_err_msg(result, alert_id_str)
            brake_alert = Brake_Alert(id=alert_id).get_alert_by_id()
            if not brake_alert: return qd_result.set_err_msg(result, '该报警邮件不存在')
            brake_alert.delete()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Brake_Config_Version_Api(object):
    '''
    @note: brake configure version class
    '''

    @jsonResponse()
    def check_upgrade(self, version=None):
        '''
        @note: using: check the tool of brake configuration's version
        @note: access method:/brake_api/Brake_Config_Version_Api/check_upgrade/
        @note: demo:{version:"1.0"}
        @param version: the tool of brake configuration's version
        @return: result:{'err': 0, 'msg': '', 'log': '', 'data': {'configure': {'md5sum': 'sfdsfdsafd', 'file_uri': 'http://sdjak.com','message':'aaaa','version': '2312313'}, 'flag': 'Y'}}
        '''
        try:
            result = qd_result.get_default_result()
            config_version = Brake_Config_Version(former_version=version, status='1')
            config_version = config_version.check_upgrade()
            if not config_version: return qd_result.set_err_msg(result, 'there is no configure version in database now')
            result['data']['configure'] = config_version.get_brake_config_version_info()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def add_version(self, former_version=None, version=None, filename=None, md5sum=None, message=None):
        '''
        @note: using: add configure version information
        @note: access method:/manage/add_brake_config_version
        @note: demo: {former_version:"1.0",version:"1.1",filename:"aaa.apk",md5sum:"sdfjskdffsjk","message":"123123"}
        @param former_version: former version
        @param version: version
        @param filename: the version file's filename
        @param message: version message
        @return: result:{'log': '', 'msg': '', 'data': {'flag': 'Y'}, 'err': 0}
        '''
        try:
            result = qd_result.get_default_result()
            version_flag, version_str = validate.validate_version(str(version))
            if not version_flag: return qd_result.set_err_msg(result, version_str)
            if former_version:
                former_version_flag, former_version_str = validate.validate_version(str(former_version))
                if not former_version_flag: return qd_result.set_err_msg(result, former_version_str)
            file_uri = "%s%s%s" % (setting_const['base']['host'], CONST['brake_config_relative_dir'], filename)

            config_version = Brake_Config_Version(former_version=former_version, version=version,
                                                  file_uri=file_uri, md5sum=md5sum, message=message, status='1')
            config_version = config_version.add_version()
            if not config_version: return qd_result.set_err_msg(result, '版本已经存在')
            result['data']['version_id'] = str(config_version.id)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_version_list(self):
        '''
        @note: using:get version list
        @note: access method:/brake_api/Brake_Config_Version_Api/get_version_list/
        @note: demo:{}
        @return: result:{'msg': '', 'data': {'version_list': [{'md5sum': 'sfdsfdsafd', 'id': '566f7938c0d20710f6733ee0', 'version': 'sfdsfsdaf', 'message': '', 'former_version': '2312313', 'file_uri': 'http://sdjak.com'}], 'flag': 'Y'}, 'log': '', 'err': 0}
        '''
        try:
            result = qd_result.get_default_result()
            config_version_list = Brake_Config_Version.objects(status="1")
            result['data']['version_list'] = [config_version.get_brake_config_version_info() for config_version in
                                              config_version_list]
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def remove_version(self, version_id=None):
        '''
        @note: using:remove version
        @note: access method:/manage/remove_brake_version
        @note: demo: {version_id:"1231232"}
        @param version_id: version id
        @return: {'err':0,'msg':'','log':'','data':{'flag':'Y'}}
        '''
        try:
            result = qd_result.get_default_result()
            config_version = Brake_Config_Version.objects(id=str(version_id)).first()
            if config_version: config_version.delete()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Brake_Configer_Api(object):
    '''
    @note: configer api
    '''

    @jsonResponse()
    def get_password(self, phone=None, get_type=1):
        """
        @note: 用途：获得闸机配置密码
        @note: 访问url： /brake_api/Brake_Configer_Api/get_password/
        @note: 测试demo:{phone:"18188621491"} 
        @param phone: 手机号
        @param get_type: 获取方式，1-短信，2-语音
        @return: result{"data":{"flag":"Y"}},Y表示添加成功，N表示添加失败
        """
        try:
            result = qd_result.get_default_result()
            if phone in ['11112222333', '12345678901']: return qd_result.set_err_msg(result, '该号码不能获取密码')

            user = Web_User.objects(phone=str(phone)).first()
            if not user: return qd_result.set_err_msg(result, '该手机号不存在')

            key = "%s_config_password" % phone
            password_dict = rc.get(key)
            if not password_dict:
                user.password_num = 1
                password = int(time.time()) % 1000000
                set_time = int(time.time())
                password_dict = {"password": password, "set_time": set_time}
                rc.set(key, pickle.dumps(password_dict), 24 * 3600)
                user.password = hashlib.md5(str(password).encode(encoding='utf8')).hexdigest()
                user.updated_time = datetime.datetime.now()
            else:
                password_dict = pickle.loads(password_dict)
                password = password_dict['password']
                if user.password_num >= 3:
                    return qd_result.set_err_msg(result, '申请次数已达上限，可凭最后一次密码在当天内继续使用')
                user.password_num += 1
            user.save()
            if int(get_type) == 1:
                hour = 24 - int((int(time.time()) - password_dict['set_time']) / 3600)
                url = 'smsRequest?body={"mobile":"%s","content":"尊敬的用户，您的配置密码是：%s，密码将在%s失效, %s"}' % \
                  (phone, password, hour, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            elif int(get_type) == 2:
                url = 'voiceVerfyCode?body={"mobile":"%s","content":"%s"}' % (phone, password)
            request_bj_server(method_url=url, method_params={}, post_flag=False)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def log_in(self, phone=None, password=None):
        """
        @note: 用途：web用户登录
        @note: 访问url： /brake_config_login_v2
        @note: 测试demo:{phone:"12345678901",password:"e10adc3949ba59abbe56e057f20f883e"}
        @param phone: 手机号
        @param password: 闸机配置密码
        @return: {"err": 0, "msg": "", "log": "", "data": {"flag": "Y", "web_user": {"project_list": [{"project_id": "91", "project": "上海蔚澜香醍", "city_id": "1", "province": "上海", "city": "上海"}]}, "server_time": 1457000435}}
        """
        try:
            result = qd_result.get_default_result()
            if not password: return qd_result.set_err_msg(result, 'password can not be empty')

            web_user = Web_User.objects(phone=str(phone), password=str(password)).first()
            if not web_user: return qd_result.set_err_msg(result, '密码错误')

            if web_user.status != "1": return qd_result.set_err_msg(result, '该用户未被激活')

            if web_user.phone != "12345678901":
                hour = int(time.time()) - int(web_user.updated_time.timestamp())
                hour = int(hour / 3600)
                if hour >= 24: return qd_result.set_err_msg(result, '已过时，禁止登录，请重新获取密码')

            result['data']['web_user'] = {'project_list': Web_User.get_access_project_info(user_obj=web_user)}
            result['data']['server_time'] = int(time.time())
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def sync_project_data(self, province=None, city=None, project=None):
        '''
        @note: usefull:sync project data
        @note: access method: /brake_api/Brake_Configer_Api/sync_project_data/
        @note: test demo:{province:"重庆",city:"重庆",project:"中天阳光美地"}
        @param province: province
        @param city: city
        @param project: project
        @return: {'test_code': 0, 'data': {'brake_machine_list': [{'mac': '112233445566', 'command': '0', 'position': {'project_list': [{'group_list': [], 'project': '千丁互联'}], 'level': 2, 'province': '西藏', 'city': '中陲'}, 'heart_time': 24, 'position_str': '千丁互联gate one入', 'wifi_rssi': '-78', 'open_time': '18', 'id': '57978adecdc8721bfdc02a59', 'bluetooth_rssi': '-78', 'province': '西藏', 'city': '中陲', 'gate_name': 'gate one', 'updated_time': 1469549278, 'version_id': '57978a8ccdc8721bf5a3f6f1', 'online_status': 1, 'direction': 'I', 'version': 'V1.1', 'is_monit': 0, 'project': '千丁互联'}], 'brake_version_list': [{'md5sum': 'test_md5', 'version': 'V1.1', 'former_version': '', 'file_uri': 'http://www.qding.cloud/uploads/brake/rom/test.test'}], 'flag': 'Y', 'basedata': {'group_list': [{'group_id': 3428808898, 'build_list': [{'unit_dict_list': [{'password_num': 1875, 'project_group_build_unit_id': 4046538762, 'unit': '11'}], 'unit_list': ['11'], 'build': '1122', 'build_id': 1450233462}], 'group': '11'}], 'project_id': 2857738755, 'project': '千丁互联'}}, 'msg': 'success', 'err': 0, 'log': ''}
        '''
        try:
            result = qd_result.get_default_result()
            if not province or not city or not project:
                return qd_result.set_err_msg(result, 'province or city or project can not be empty')

            project_obj = Basedata_Project.objects(province=province, city=city, project=project).first()
            if not project_obj: return qd_result.set_err_msg(result, 'the project you choose not exists')

            unit_obj = Basedata_Unit.objects(outer_project_id=project_obj.outer_project_id).first()
            if not unit_obj: return qd_result.set_err_msg(result, "the project you choose has no unit data")

            key = "%sinit_project_data" % project_obj.outer_project_id
            basedata_str = rc.get(key)

            if not basedata_str:
                project_dict = unit_obj.get_project_dict()
                rc.set(key, pickle.dumps(project_dict))
            else:
                project_dict = pickle.loads(basedata_str)
            result['data']['basedata'] = project_dict
            brake_version_list = Brake_Version.get_version_list_for_config(province=province, city=city, project=project)
            result['data']['brake_version_list'] = brake_version_list
            brake_machine_list = Brake_Machine.get_project_brake(province=province, city=city, project=project)
            result['data']['brake_machine_list'] = brake_machine_list
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def sync_project_data_by_id(self, outer_project_id_list=[]):
        '''
        @note: usefull:sync project data by id
        @note: access method: /brake_api/Brake_Configer_Api/sync_project_data_by_id/1/
        @note: test demo: {"outer_project_id_list":['1879']}
        @param outer_project_id_list: outer project id list
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            opil_flag, opil, opil_str = validate.validate_outer_project_id_list(outer_project_id_list)
            if not opil_flag: return qd_result.set_err_msg(result, opil_str)

            project_data_list = []
            check_list = []
            for outer_project_id in opil:
                unit_obj = Basedata_Unit.objects(outer_project_id=outer_project_id).first()
                if not unit_obj: return qd_result.set_err_msg(result, "您选取的项目中存在单元数据不存在的项目，%s" % outer_project_id)

                key = "%sinit_project_data" % outer_project_id
                basedata = rc.get(key)
                if basedata:
                    basedata = pickle.loads(basedata)
                    check_list.append((False, basedata, outer_project_id))
                else:
                    check_list.append((unit_obj, {}, outer_project_id))

            for unit_obj, basedata, outer_project_id in check_list:
                if unit_obj:
                    basedata = unit_obj.get_project_dict()
                    key = "%sinit_project_data" % outer_project_id
                    rc.set(key, pickle.dumps(basedata))
                project_dict = {
                    "basedata": basedata,
                    "brake_machine_list": Brake_Machine.get_project_brake(outer_project_id=outer_project_id),
                    "brake_version_list": Brake_Version.get_version_list_for_config(outer_project_id=outer_project_id)
                }
                project_data_list.append(project_dict)

            result['data']['project_data_list'] = project_data_list

        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def add_brake(self, position=None, gate_info=None, mac=None, bluetooth_rssi=None, wifi_rssi=None,
                  open_time=None, version=None, hardware_version=None):
        """
        @note: usefull: add brake
        @note: access method:/brake_api/Brake_Configer_Api/add_brake/1/
        @note: position level: 0-province,1-city,2-project,3-group,4-build,5-unit,6-floor,7-room
        @note: test demo: {'position':'{"province": "江苏", "project_list": [{"group_list": "[]", "project": "紫云台"}], "city": "无锡", "level": "2"}', 'gate_info':'{"direction": "I", "gate_name": "test门"}', "mac":112233445566, "bluetooth_rssi":-100,"wifi_rssi":-100,"open_time":50,"version":"V1.1", "hardware_version":"QC202-v1"}
        @param position: position, can only be dict
        @param gate_info: gate info, can only be dict
        @param mac: mac address
        @param bluetooth_rssi: bluetooth rssi
        @param wifi_rssi:wifi rssi
        @param open_time: open time
        @param version: version
        @param hardware_version: hardware version
        @return: {"msg": "", "data": {"flag": "Y","brake_id":"12312323"},"log": "", "err": 0}
        """
        try:
            result = qd_result.get_default_result()
            result['data']['brake_id'] = ""
            position = json.loads(position) if isinstance(position, str) else position
            gate_info = json.loads(gate_info) if isinstance(gate_info, str) else gate_info

            validate_position_flag, validate_position_str = validate.validate_position(position)
            if not validate_position_flag: return qd_result.set_err_msg(result, validate_position_str)

            validate_gate_info_flag, validate_gate_info_str = validate.validate_gate_info(gate_info)
            if not validate_gate_info_flag: return qd_result.set_err_msg(result, validate_gate_info_str)

            mac_flag, mac_str = validate.validate_mac(str(mac))
            if not mac_flag: return qd_result.set_err_msg(result, mac_str)

            bluetooth_rssi_flag, bluetooth_rssi_str = validate.validate_bluetooth_rssi(str(bluetooth_rssi))
            if not bluetooth_rssi_flag: bluetooth_rssi = '-76'

            wifi_rssi_flag, wifi_rssi_str = validate.validate_wifi_rssi(str(wifi_rssi))
            if not wifi_rssi_flag: wifi_rssi = '-76'

            open_time_flag, open_time_str = validate.validate_open_time(str(open_time))
            if not open_time_flag: open_time = '5'

            hardware_version_re = re.compile("^QC.*")
            if hardware_version and not hardware_version_re.match(hardware_version): hardware_version = "QC201_V1.1"

            position_str = Brake_Machine.make_position_str(position, gate_info)
            brake_machine = Brake_Machine(position=position, position_str=position_str, mac=mac,
                                          gate_info=gate_info, bluetooth_rssi=str(bluetooth_rssi),
                                          wifi_rssi=str(wifi_rssi), open_time=str(open_time), firmware_version=version,
                                          hardware_version=hardware_version, configure_time=datetime.datetime.now(),
                                          configure_user=self.qz_session['_session_cache'].get('phone'))

            brake = brake_machine.add_brake_by_configer()
            if not brake: return qd_result.set_err_msg(result, 'add brake fail')

            result['data']['brake_id'] = str(brake.id)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Brake_Card_Api(object):
    '''
    @note brake card api class
    '''

    @jsonResponse()
    def read_card(self, card_no=None, card_sn=None):
        '''
        @note: access method : /brake_api/Brake_Card_Api/read_card/
        @param card_no: card no,1-10 digits
        @param card_sn: card sn,1-10 hex digits
        @return:
        '''
        try:
            result = qd_result.get_default_result()

            card_obj = Brake_Card(card_no=int(card_no))
            from apps.common.utils.qd_encrypt import set_basedata_id
            enc_card_no, count = set_basedata_id(str(card_sn), card_obj.check_card_no_unique)
            result['data']['enc_card_no'] = enc_card_no

            result['data']['count'] = count
            db_card_obj= Brake_Card.objects(status="1", card_no=int(card_no)).first()
            if not db_card_obj: return qd_result.set_err_msg(result, "不存在", flag='Y')

            result['data']['card_obj_info'] = {
                "card_area": db_card_obj.card_area,
                "card_owner": db_card_obj.card_owner,
                "card_validity": int(db_card_obj.card_validity.timestamp()),
                "card_type": db_card_obj.card_type,
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_write_no(self, card_info={}, id_info={}):
        '''
        @note: access method: /brake_api/Brake_Card_Api/get_write_no/1/
        @param card_info: {"enc_card_no":"xx123", "enc_card_no_count":123, "card_no":123123,"card_type":1,"card_validity":1234567890}
        @param id_info: {"project_id_list":[{"project_id":123123,"group_id":123,"build_id":12312,"unit_id":123123}],"room_id_list": ["123123"]}
        @return: {'data': {'flag': 'Y', 'write_no': 'e9f7000159584ab3'}, 'log': '', 'msg': 'success', 'err': 0, 'test_code': 0}
        '''
        try:
            result = qd_result.get_default_result()

            card_info = json.loads(card_info) if isinstance(card_info, str) else card_info
            card_info_check_flag, card_info_check_str = validate.validate_card_info(card_info)
            if not card_info_check_flag: return qd_result.set_err_msg(result, card_info_check_str)

            id_info = json.loads(id_info) if isinstance(id_info, str) else id_info
            id_info_check_flag, id_info_check_str = validate.validate_id_info(id_info, int(card_info['card_type']))
            if not id_info_check_flag: return qd_result.set_err_msg(result, id_info_check_str)

            write_no = Brake_Card.get_write_no(card_info, id_info)
            if not write_no: return qd_result.set_err_msg(result, 'get write number failed')

            result['data']['write_no'] = write_no
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def open_card(self, card_info=None, id_info=None, owner_info=None):
        '''
        @note: access method: /brake_api/Brake_Card_Api/open_card/
        @note: card type: 1-project card, 2-group card, 3-build_card, 4-unit_card
        @note: card_validity: 1-one month, 2-half past year, 3-forever
        @note: gender: can only be F or M
        @param card_info: {"enc_card_no":"xx123", "enc_card_no_count":123, "card_no":123123,"card_type":1234567890,"card_validity":1}
        @param id_info: {"project_id_list":[{"project_id":123123,"group_id":123,"build_id":12312,"unit_id":123123}],"room_id_list": ["123123"]}
        @param owner_info: {"name":"julian", "gender":"M", "phone":"12345678901"}
        @return: {'data': {'flag': 'Y'}, 'log': '', 'msg': 'success', 'err': 0, 'test_code': 0}
        '''
        try:
            result = qd_result.get_default_result()

            card_info = json.loads(card_info) if isinstance(card_info, str) else card_info
            card_info_check_flag, card_info_check_str = validate.validate_card_info(card_info)
            if not card_info_check_flag: return qd_result.set_err_msg(result, card_info_check_str)

            id_info = json.loads(id_info) if isinstance(id_info, str) else id_info
            id_info_check_flag, id_info_check_str = validate.validate_id_info(id_info, int(card_info['card_type']))
            if not id_info_check_flag: return qd_result.set_err_msg(result, id_info_check_str)

            owner_info = json.loads(owner_info) if isinstance(owner_info, str) else owner_info
            owner_info_check_flag, owner_info_check_str = validate.validate_owner_info(owner_info)
            if not owner_info_check_flag: return qd_result.set_err_msg(result, owner_info_check_str)

            card_obj, ret_str = Brake_Card().set_card_while_open_card(card_info, id_info, owner_info)

            if not card_obj: return qd_result.set_err_msg(result, ret_str)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def delete_card(self, card_no=None):
        '''
        @note: access method: /brake_api/Brake_Card_Api/delete_card/
        @param card_no: card no
        @return: {'err': 0, 'msg': 'success', 'log': '', 'data': {'flag': 'Y'}}
        '''
        try:
            result = qd_result.get_default_result()

            db_card_obj, ret_str = Brake_Card.get_card_obj_by_card_no(card_no=card_no)
            if not db_card_obj: return qd_result.set_err_msg(result, ret_str)

            db_card_obj.delete_card_obj()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_black_and_white_list(self, outer_app_user_id=None):
        '''
        @note: access method /brake_api/Brake_Card_Api/get_black_and_white_list/
        @note: test_demo: {"outer_app_user_id": "ff8080815baeb4cf015baec66d8213cd"}
        @param outer_app_user_id: outer app user id
        @return: {'err': 0, 'black_list': [{"card_no":1111111,"updated_time":2222222}], 'white_list':[{"card_no":33333333, "updated_time":4444444}], 'msg': 'success', 'data': {'flag': 'Y'}, 'log': ''}
        '''
        try:
            result = qd_result.get_default_result()
            app_user, ret_str = Basedata_BJ_App_User(outer_app_user_id=outer_app_user_id).get_app_user_by_outer_app_user_id(1498724908)
            if not app_user: return qd_result.set_err_msg(result, "outer_app_user_id %s not exists" % outer_app_user_id)

            outer_project_list = [room['outer_project_id'] for room in app_user.room_data_list if room['outer_project_id']]

            black_list, white_list = [], []
            for outer_project_id in outer_project_list:
                black_list.extend(Brake_Card.get_black_or_white_card_obj_list(outer_project_id=outer_project_id, status="2"))
                white_list.extend(Brake_Card.get_black_or_white_card_obj_list(outer_project_id=outer_project_id, status="4"))

            result['data']['black_list'] = black_list
            result['data']['white_list'] = white_list
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def clear_or_add_open_door_list(self, operate_list=None):
        '''
        @note: access method: /brake_api/Brake_Card_Api/clear_or_add_open_door_list/
        @note: test demo: {"operate_list": '[{"mac":"112233445566","white_card_no_list":[111222],"black_card_no_list":[556677]}]'}
        @param operate_list: operate list, demo: [{"mac":"112233445566","card_no_list":[111222]}], all list length must less than 10
        @return: {'err': 0, 'msg': 'success', 'log': '', 'data': {'flag': 'Y'}}
        '''
        try:
            result = qd_result.get_default_result()

            operate_list = json.loads(operate_list) if isinstance(operate_list, str) else operate_list
            validate_clear_list_flag, validate_clear_list_str = validate.validate_clear_list(operate_list)
            if not validate_clear_list_flag: return qd_result.set_err_msg(result, validate_clear_list_str)

            for operate_list_dict in operate_list:
                validate_clear_list_flag, validate_clear_list_str = validate.validate_clear_list_dict(operate_list_dict)
                if not validate_clear_list_flag: return qd_result.set_err_msg(result, validate_clear_list_str)

                mac = operate_list_dict['mac']
                white_card_no_list = operate_list_dict['white_card_no_list']
                black_card_no_list = operate_list_dict['black_card_no_list']

                db_brake_machine = Brake_Machine.get_brake_by_mac(mac=mac)
                if not db_brake_machine: continue
                brake_machine = Brake_Machine.get_brake_info_for_pass(db_brake_machine)

                Brake_Card.check_status(brake_machine, black_card_no_list, white_card_no_list)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_card_by_filter(self, card_type=None, status=None, province=None, city=None,
                           project=None, group=None, build=None, unit=None, room=None,
                           card_no=None, phone=None, name=None, card_id=None, page_no=1, page_size=30):
        '''
        @note: access url: /brake_api/Brake_Card_Api/get_card_by_filter/1/
        @param card_id: card id
        @param card_type: card type
        @param status: status
        @param province: province
        @param city: city
        @param project: project
        @param group: group
        @param build: build
        @param unit: unit
        @param room: room
        @param card_no: card_no
        @param phone: phone
        @param name: name
        @param all_flag: get all record
        @param page_no: page number
        @param page_size: page size
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            page_flag, page_str = validate.validate_pagination(str(page_size), str(page_no))
            if not page_flag: return qd_result.set_err_msg(result, page_str)

            card_obj_list = Brake_Card.get_card_by_filter(card_id, card_type, status, province,
                                                          city, project, group, build, unit, room,
                                                          card_no, phone, name, page_no, page_size)
            card_obj_info_list = []
            if card_obj_list:
                for card_obj in card_obj_list:
                    card_obj.set_door_list()
                    card_obj.save()
                    card_obj_info_list.append(card_obj.get_card_obj_info())
                total_count = card_obj_list.count()
            else:
                total_count = 0
            result['data']['card_list'] = card_obj_info_list
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': total_count,
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def modify_card(self, card_id=None, phone=None, name=None, status=None):
        '''
        @note: usefull, modify card
        @note: access url: /brake_api/Brake_Card_Api/modify_card/1/
        @param card_id: card id
        @param phone: phone
        @param name: name
        @param status: status : 1-激活，2-注销中，3-已注销，4-激活中
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            db_card_obj = Brake_Card.objects(id=str(card_id)).first()
            if not db_card_obj: return qd_result.set_err_msg(result, '%s 不存在' % card_id)

            if phone:
                phone_flag, phone_str = validate.validate_phone(phone)
                if not phone_flag: return qd_result.set_err_msg(result, phone_str)

            if name:
                name_flag, name_str = validate.validate_str("姓名", name)
                if not name_flag: return qd_result.set_err_msg(result, name_str)

            if status:
                status_flag, status_str = validate.validate_status(status)
                if not status_flag: return qd_result.set_err_msg(result, status_str)

            db_card_obj.modify_card_obj(phone, name, status)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_card_info(self, card_no):
        '''
        @note: usefull: 获取门禁卡的信息
        @note: access url: /brake_api/Brake_Card_Api/get_card_info/
        @param card_no:
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            card_obj = Brake_Card.objects(card_no=int(card_no)).first()
            if not card_obj: return qd_result.set_err_msg(result, '该卡号不存在')

            if not card_obj.door_list: card_obj.set_door_list()
            result['data']['card_obj'] = card_obj.get_card_obj_info()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_can_open_door_list(self, card_no):
        '''
        @note: usefull: 获取开门列表
        @note: access url: /brake_api/Brake_Card_Api/get_can_open_door_list/
        @param card_no: card no
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            card_obj = Brake_Card.objects(card_no=int(card_no)).first()
            door_list = []
            if card_obj: door_list = card_obj.door_list
            result['data']['door_list'] = door_list
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def set_can_open_door_list(self, card_no):
        '''
        @note: usefull: 设置开门列表
        @note: access url: /brake_api/Brake_Card_Api/set_can_open_door_list/
        @param card_no:
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            card_obj = Brake_Card.objects(card_no=int(card_no)).first()
            if card_obj:
                card_obj.set_door_list()
                card_obj.save()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def app_get_write_no(self, card_info={}, owner_info={}, room_id_list=[], action="add"):
        '''
        @note: usefull: app获取写卡数据
        @note: access url: /brake_api/Brake_Card_Api/app_get_write_no/
        @note: test demo: {"action":"modify","card_info":"{"card_no":"04D5981ACB5280","card_type":"5","card_validity":1505750400}","owner_info":"{"name":"小魏","phone":"13810305684"}","room_id_list":"["31605161452529","31605161411349"]"}
        @param card_info: {"card_no":"1245141264978561","card_type":5,"card_validity":1234567890}
        @param owner_info: {"name":"test","phone":"12345678901"}
        @param room_id_list: [713001]
        @param action: can only be "add" or "modify"
        @return: {'test_code': 0, 'data': {'flag': 'Y', 'write_no': 'ccb200028eb'}, 'msg': 'success', 'err': 0, 'log': ''}
        '''
        try:
            result = qd_result.get_default_result()

            card_info = json.loads(card_info) if isinstance(card_info, str) else card_info
            card_info_flag, card_info_str = validate.validate_app_card_info(card_info)
            if not card_info_flag: return qd_result.set_err_msg(result, card_info_str)

            owner_info = json.loads(owner_info) if isinstance(owner_info, str) else owner_info
            owner_info_flag, owner_info_str = validate.validate_app_owner_info(owner_info)
            if not owner_info_flag: return qd_result.set_err_msg(result, owner_info_str)

            room_id_list = json.loads(room_id_list) if isinstance(room_id_list, str) else room_id_list
            room_id_list_flag, room_id_list_str = validate.validate_room_id_list(room_id_list)
            if not room_id_list_flag: return qd_result.set_err_msg(result, room_id_list_str)

            if action not in ['add', 'modify']:
                return qd_result.set_err_msg(result, "the action can only be add or modify")

            card_no = int(str(card_info['card_no']), 16)
            card_sn = card_info['card_no'].rjust(14, '0')
            card_info['card_no'] = card_no
            card_obj = Brake_Card(card_no=card_no)

            from apps.common.utils.qd_encrypt import set_basedata_id
            card_obj.enc_card_no, count = set_basedata_id(str(card_sn), card_obj.check_card_no_unique)

            card_info.update({
                "enc_card_no": card_obj.enc_card_no,
                "enc_card_no_count": count,
            })
            id_info = {"room_id_list": room_id_list}

            card_obj, ret_str = card_obj.set_card_while_open_card(card_info, id_info, owner_info)
            if not card_obj: return qd_result.set_err_msg(result, ret_str)

            if card_obj.status in ["2", "3"]:
                card_obj.status = "4"
                card_obj.save()
            result['data']['write_no'] = Brake_Card.get_write_no(card_info, id_info)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class Brake_Open_Time_Api(object):
    '''

    '''
    @jsonResponse()
    def uploads(self, record_list=[]):
        '''
        @note: usefull: uploads open time record
        @note: access method:/brake_api/Brake_Open_Time_Api/uploads/
        @note: test demo:[{"app_device_info": {"app_version": "2.1.0","device_model": "samsungSM-N9002","platform": "android","platform_version": "4.3"},"machine_mac": "883B8B011A2F","outer_app_user_id": "ac04d83278a011e58a30418610535297","pass_info": {"pass_type": "0","pass_result_code": 0,"pass_time": 1500627316,"pass_mode": 100},"pass_time_cost": {"0": 661,"10": 5,"11": 4,"12": 157,"16": 145,"17": 343}}]
        @param record_list: record list
        @return:
        '''
        try:
            result = qd_result.get_default_result()
            record_list, ret_str = validate.validate_record_list(record_list)
            if not record_list: return qd_result.set_err_msg(result, ret_str)
            for record in record_list:
                bot = Brake_Open_Time()
                bot.outer_app_user_id = record['outer_app_user_id']
                bot.machine_mac = record.get('machine_mac')
                bot.pass_info = record['pass_info']
                bot.pass_time_cost = record['pass_time_cost']
                bot.app_device_info = record['app_device_info']
                bot.save()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result
