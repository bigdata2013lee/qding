# coding=utf-8
import logging

import datetime
import re

from apis.aptm import AptmQueryApi
from apis.base import BaseApi
from utils import tools
from utils.qd import QdRds
from utils.tools import get_default_result, rds_api_cache
from models.aptm import Room
from models.device import AlarmGateway, AlarmArea
from models.record import AlarmRecord, AgwBcfNotice, AgwOffLineNotice, WarningRecord
from utils import misc
from utils import qd
from utils.tools import paginate_query_set
from utils.permission import app_user_login_required, common_login_required, wuey_user_login_required

log = logging.getLogger('django')
__doc__ = """
api module name: agw
"""

class AGWDeviceApi(BaseApi):
    """
    与网关设备相关
    """

    def _create_update_dev(self, aptm_id, dev_uid, mac, alarm_areas=[]):
        """
        创建网关设备,包涵设备的基本信息及防区、布防状态
        :param aptm_id: T-string, 房间编号
        :param dev_uid: T-string, 设备编号
        :param sn: T-string, 设备SN
        :param mac: T-string, 设备MAC
        :param alarm_areas: T-list[{alarm_id#int,alarm_type:#int,
                            conn_type:#int,enable:#boolean,loc_name:#string},...], 设备编号
        :return: data ->  (#bool,#str)

        """

        dev = AlarmGateway.objects(dev_uid=dev_uid).first()
        aptm = Room.objects(id=aptm_id).first()

        if not aptm:
            log.warning("无法匹配房间, dev_uid:%s, aptm_id:%s", dev_uid, aptm_id)
            return False, "无法匹配房间%s" % aptm_id

        exist_dev = AlarmGateway.objects(aptm=aptm).first()
        if not dev:
            dev = AlarmGateway()

        # 解除旧设备与房间关系， 发通知，清除房间信息
        if exist_dev and exist_dev != dev:
            RecordApi()._notice_agw_unbind(exist_dev, exist_dev.aptm)
            exist_dev.clear_aptm_infos()

        dev.set_attrs(domain=aptm.domain, project=aptm.project, aptm=aptm, aptm_uuid=aptm.aptm_uuid)
        dev.set_attrs(dev_uid=dev_uid, mac=(mac or "").upper())

        _alarm_areas = []
        _alarm_ids = []

        try:
            for area in alarm_areas:
                _area = AlarmArea.make_from_dict(area)
                _alarm_areas.append(_area)
                _alarm_ids.append(_area.alarm_id)

        except Exception as e:
            log.exception(e)
            return False, "参数异常"

        if len(set(_alarm_ids)) < len(_alarm_ids):
            return False, "重复配置防区"

        dev.alarm_areas = _alarm_areas
        dev.saveEx()
        return True, ""

    def _heartbeat(self, dev_uid, net="Wi-Fi", mac="", sw_version="", hw_version="", res_version=""):
        dev = AlarmGateway.objects(dev_uid=dev_uid).first()

        if not dev:
            log.warning("_heartbeat -> Can not found agw[dev_ud:%s]", dev_uid)
            return False

        ostatus = dev.heartbeat.get("status", "up")
        dev.heartbeat = {"status": 'up', 'at': datetime.datetime.now()}

        if mac: dev.mac = mac.upper()
        dev.net = net
        dev.set_attrs(sw_version=sw_version, hw_version=hw_version, res_version=res_version)

        dev.saveEx()
        tools.set_dev_heartbeat_ex_timer('agw', dev.id, net=net)

        if ostatus != 'up':
            evt_data = dict(dev=dev.outputEx(), status='up', dev_type=AlarmGateway.__name__)
            qd.QDEvent("device_heartbeat_status_change", data=evt_data).broadcast()

        return True

    def _update_wifi_version(self, dev_uid, version=""):
        """
        更新设备wifi版本
        :param dev_uid:
        :param version:
        :return:
        """
        dev = AlarmGateway.objects(dev_uid=dev_uid).first()

        if not dev:
            log.warning("_heartbeat -> Can not found agw[dev_ud:%s]", dev_uid)
            return False

        dev.wifi_version = version
        dev.saveEx()

        return True

    @app_user_login_required
    def user_set_agw_bcf_for_batch(self, agw_ids=[], enable=True):
        """
        用户对多个设备布撤防
        :param agw_ids: T-list[#string], 网关设备ID List
        :param enable: T-boolean, true-布防， false-撤防
        :return: data->{}

        :notice: 发送广播通知
        """

        result = get_default_result()
        _t = misc.AlarmTypesEnum
        _enable = True if enable else False
        if not agw_ids: return result

        user = self._get_login_user()
        record_api = RecordApi()

        def _(dev):

            for aa in dev.alarm_areas:
                if aa.alarm_type not in [_t.ir, _t.door, _t.window]: continue
                aa.enable = _enable

            dev.saveEx()
            notice = AgwBcfNotice(device=dev, aptm=dev.aptm, op_enable=_enable,
                                  op_user_id_desc="%s:%s" % (user.__class__.__name__, user.id))
            record_api._notice_agw_bcf(notice, user)

        for agw_id in agw_ids:
            dev = AlarmGateway.objects(id=agw_id).first()
            if not dev:
                log.warning("Not found device by agw_id: %s", agw_id)
                continue

            _(dev)


        return result

    def set_agw_alarm_enable(self, agw_id, alarm_id, enable=True):
        """
        报警网关布撤防
        :param agw_id: T-string, 报警网关设备ID
        :param alarm_id: T-string|list, 端口线路ID,或ID列表
        :param enable: T-boolean, true-布防， false-撤防
        :return:data->{}
        """
        result = get_default_result()
        _enable = True if enable else False
        alarm_ids = alarm_id if isinstance(alarm_id, list) else [alarm_id]
        dev = AlarmGateway.objects(id=agw_id).first()
        if not dev: return result.setmsg("无法匹配设备%s" % agw_id, 3)

        for alarm_id in alarm_ids:
            area = dev.get_alarm_area(alarm_id)
            if not area: continue
            area.enable = _enable

        dev.saveEx()

        return result

    @wuey_user_login_required
    def set_agw_alarm_areas_enable(self, agw_id, items=[]):
        """
        处理批量设置的布撤状态处理（for wuye）
        :param dev_uid:
        :param items: T-list[(fq_id#int, enable#int), ...], 布撤防状态
        :return: T-boolean
        """
        result = get_default_result()
        user = self._get_login_user()
        dev = AlarmGateway.objects(id=agw_id).first()
        if not dev:
            log.warning("Can not match dev by agw_id:%s", agw_id)
            return False

        change_areas=[]
        for item in items:
            area = dev.get_alarm_area(item[0])
            if not area: continue
            _enable = bool(item[1])
            if area.enable == _enable: continue

            area.enable = _enable
            change_areas.append(area)

        dev.saveEx()

        # 记录并发送布撤防通知
        record_api = RecordApi()
        for area in change_areas:
            bcf = AgwBcfNotice(device=dev, aptm=dev.aptm, op_enable=area.enable)
            record_api._notice_agw_bcf(bcf, user, area=area)

        result.setmsg("保存设置成功")
        return result

    def _set_agw_alarm_enable_for_dev(self, dev_uid, items=[]):
        """
        处理设备端上报的布撤状态处理（for agw device）
        :param dev_uid:
        :param items: T-list[(fq_id#int, enable#int), ...], 布撤防状态
        :return: T-boolean
        """

        dev = AlarmGateway.objects(dev_uid=dev_uid).first()
        if not dev:
            log.warning("Can not match dev by dev_uuid:%s", dev_uid)
            return False

        for item in items:
            area = dev.get_alarm_area(item[0])
            if not area: continue
            area.enable = bool(item[1])
            area.delay_alarm_ts = item[2]

        dev.saveEx()

        # 记录并发送布撤防通知
        record_api = RecordApi()
        op_enable = bool(items[0][1]) if items else False
        bcf = AgwBcfNotice(device=dev, aptm=dev.aptm, op_enable=op_enable)
        record_api._notice_agw_bcf(bcf, None, area=None, is_from_dev=True)

        return True

    @common_login_required
    def set_agw_alarm_area(self, agw_id, alarm_id, enable=True, delay_enable_ts=0, delay_alarm_ts=0):
        """
        单路防区设置
        :param agw_id:  T-string, 报警网关设备ID
        :param alarm_id: T-string, 端口线路ID
        :param enable: T-boolean, T-boolean, true-布防， false-撤防
        :param delay_enable_ts: T-int, 布防延时
        :param delay_alarm_ts: T-int, 报警延时
        :return: data->{}
        """
        result = get_default_result()
        user = self._get_login_user()
        dev = AlarmGateway.objects(id=agw_id).first()

        record_api = RecordApi()

        if not dev:
            return result.setmsg("无法匹配设备%s" % agw_id, 3)

        area = dev.get_alarm_area(alarm_id)
        if not area: return result.setmsg("无法匹配防区%s" % alarm_id, 3)

        area.enable = True if enable else False
        area.delay_enable_ts = delay_enable_ts
        area.delay_alarm_ts = delay_alarm_ts

        # 记录并发送布撤防通知
        bcf = AgwBcfNotice(device=dev, aptm=dev.aptm, op_enable=area.enable)
        record_api._notice_agw_bcf(bcf, user, area=area)

        dev.saveEx()

        return result

    def set_agw_name(self, agw_id, name=""):
        """
        用户设备网关设备的别名
        :param agw_id: T-string, 报警网关设备ID
        :param name: T-string, 报警网关设备别名
        :return: data->{}
        """

        result = get_default_result()

        dev = AlarmGateway.objects(id=agw_id).first()
        if not dev:
            return result.setmsg("无法匹配设备%s" % agw_id, 3)

        if name: dev.name = name
        dev.saveEx()

        return result


class AGWDeviceQueryApi(BaseApi):

    def _sync_agw_infos_for_dev(self, dev_uid):
        """
        设备同步防区配置,版本信息，解绑状态
        :return:
        """

        dev = AlarmGateway.objects(dev_uid=dev_uid).first()
        res = {"bu_fang_list": [], "is_bind_aptm": False}
        if not dev:
            log.warning("_sync_agw_infos_for_dev -> Can not fond agw[dev_uid:%s]", dev_uid)
            return res

        if dev.aptm:
            res["is_bind_aptm"] = True

        alarm_areas = dev.alarm_areas
        res["bu_fang_list"] = [(aa.alarm_id, 1 if aa.enable else 0, aa.delay_alarm_ts, aa.delay_enable_ts) for aa in alarm_areas]
        return res

    def get_dev_by_mac(self, macs=[]):
        """
        通过mac，获取设备list
        :param macs:T-list[#string], 报警网关设备MAC List
        :return:　data->{collection:[{#obj},...]}
        :notice: 供配置工具使用的接口
        """
        result = get_default_result()

        devs = AlarmGateway.objects(mac__in=macs)
        result.data['collection'] = []
        for dev in devs:
            json_out = dev.outputEx()
            aptm_loc_infos = {}
            if dev.aptm:
                aptm_loc_infos = AptmQueryApi()._get_aptm_loc_infos(dev.aptm.id)
            json_out['aptm_loc_infos'] = aptm_loc_infos
            result.data_collection.append(json_out)

        return result

    def list_agw_devices(self, project_id, phase_no=0, building_no=0, aptm_short_code="", pager={}):
        """
        网关设备分页查询
        :param phase_no: T-int, 期编号
        :param building_no: T-int, 楼栋编号
        :param aptm_short_code: T-str, 房间号
        :param pager:T-object{page_no:#int, page_size:#int}, 分页参数
        :return:
        """
        result = get_default_result()
        conditions = {"project": project_id}

        codes = [phase_no, building_no, 0, 0, 0]

        if aptm_short_code:
            codes[3:] = tools.parse_aptm_short_code(aptm_short_code)

        aptm_pattern = tools.parse_codes_to_aptm_uuid_pattern(codes)

        conditions.update({"aptm_uuid": re.compile(aptm_pattern)})

        devs = AlarmGateway.objects(**conditions)
        result.data = paginate_query_set(devs, pager)
        return result

    def list_agws_by_aptm(self, aptm_id):
        """
        列出某房间(或多个房间)下，所有网关设备
        :param aptm_id:T-string|list, 房间ID | 房间ID List
        :return:data->{collection:[...]}
        """
        result = get_default_result()
        result.data_collection = []
        aptm_ids = []
        if isinstance(aptm_id, str):
            aptm_ids.append(aptm_id)
        elif isinstance(aptm_id, list):
            aptm_ids = aptm_id

        devs = AlarmGateway.objects(aptm__in=aptm_ids)[:100]
        result.data_collection = []
        for dev in devs:
            result.data_collection.append(dev.outputEx())
        return result

    def check_aptm_has_agw(self, aptm_id):
        """
        检查房间是否已经存在网关设备
        如果存在，返回设备的基本信息list，否则返回空list
        :param aptm_id: T-string, 房间ID
        :return: data->{dev_uids:["dev_uids", ...]}
        """

        result = get_default_result()
        result.setdata("dev_uids", [])
        dev = AlarmGateway.objects(aptm=aptm_id).first()
        if dev:
            result.setdata("dev_uids", ["%s" % dev.dev_uid])

        return result


    def get_agw(self, agw_id):
        """
        通过设备ID，获取设备
        :param agw_id: T-string, 报警网关设备ID
        :return: data->{agw:{#obj}}
        """

        result = get_default_result()
        dev = AlarmGateway.objects(id=agw_id).first()
        if not dev:
            return result.setmsg("无法找到设备:%s" % agw_id, 3)

        result.data['agw'] = dev.outputEx()
        return result


class AlarmApi(BaseApi):
    """
    与报警记录相关
    """

    def create_alarm(self, dev_uid, alarm_id, alarm_type):
        """
        创建报警记录
        :param dev_uid:T-string, 网关设备UID
        :param alarm_id:T-string, 防区端口
        :param alarm_type:T-string, 报警类型
        :return:data->{}
        """
        result = get_default_result()
        now = datetime.datetime.now()
        alarm = AlarmRecord(alarm_id=alarm_id, alarm_type=alarm_type)
        device = AlarmGateway.objects(dev_uid=dev_uid).first()
        if not device:
            log.warning("无法生成报警记录，设备dev_uid:%s不存在", dev_uid)
            return result.setmsg("无法生成报警记录，设备dev_uid:%s不存在" % dev_uid, 3)

        aptm = device.aptm
        if not aptm:
            log.warning("dev_uid:%s未找到对应房间", dev_uid)
            return result.setmsg("dev_uid:%s未找到对应房间" % dev_uid, 3)

        alarm.set_attrs(domain=aptm.domain, project=aptm.project, aptm=aptm, device=device)
        alarm.set_attrs(aptm_uuid=aptm.aptm_uuid, aptm_name=aptm.name, aptm_pre_names=aptm.get_aptm_pre_names())

        dt_str = "{0}月{1}日 {2:0>2}:{3:0>2}".format(now.month, now.day, now.hour, now.minute)
        alarm_area = device.get_alarm_area(alarm_id)

        loc_name = alarm_area.loc_name if alarm_area else ""
        alarm_type_name = misc.Alarm_Types_ZH.get(alarm_type, "")

        alarm.alarm_type_name = alarm_type_name
        alarm.name = "%s 在%s%s发生%s报警" % (dt_str, aptm.name, loc_name, alarm_type_name)
        alarm.saveEx()

        qd.QDEvent("trigger_agw_alarm", project_id=alarm.project.id, data=alarm.outputEx()).broadcast()

        return result


    def create_warning(self, dev_uid, alarm_id, alarm_type):
        """
        创建警告记录
        :param dev_uid:T-string, 网关设备UID
        :param alarm_id:T-string, 防区端口
        :param alarm_type:T-string, 报警类型
        :return:data->{}
        """
        result = get_default_result()
        now = datetime.datetime.now()
        warning = WarningRecord(alarm_id=alarm_id, alarm_type=alarm_type)
        device = AlarmGateway.objects(dev_uid=dev_uid).first()
        if not device:
            log.warning("无法生成警告记录，设备dev_uid:%s不存在", dev_uid)
            return result.setmsg("无法生成警告记录，设备dev_uid:%s不存在" % dev_uid, 3)

        aptm = device.aptm
        if not aptm:
            log.warning("dev_uid:%s未找到对应房间", dev_uid)
            return result.setmsg("dev_uid:%s未找到对应房间" % dev_uid, 3)

        warning.set_attrs(domain=aptm.domain, project=aptm.project, aptm=aptm, device=device)
        warning.set_attrs(aptm_uuid=aptm.aptm_uuid, aptm_name=aptm.name, aptm_pre_names=aptm.get_aptm_pre_names())

        dt_str = "{0}月{1}日 {2:0>2}:{3:0>2}".format(now.month, now.day, now.hour, now.minute)
        alarm_area = device.get_alarm_area(alarm_id)

        alarm_type_name = misc.Alarm_Types_ZH.get(alarm_type, "")
        warning.alarm_type_name = alarm_type_name

        loc_name = alarm_area.loc_name if alarm_area else "房间"
        warning.name = "%s 在%s%s发生%s延时报警" % (dt_str, aptm.name, loc_name, misc.Alarm_Types_ZH.get(alarm_type, ""))
        warning.saveEx()

        # qd.QDEvent("trigger_agw_warning", project_id=warning.project.id, data=warning.outputEx()).broadcast()
        return result

    def set_alarm_dealed(self, alarm_oid, desc=""):
        """
        把报警设置为已处理，并进行说明
        :param alarm_oid: T-string, 报警记录ID
        :param desc:T-string, 报警处理说明
        :return:data->{}
        """
        result = get_default_result()
        alarm = AlarmRecord(id=alarm_oid).first()
        if not alarm:
            return result.setmsg("无法匹配记录%s" % alarm_oid, 3)

        alarm.deal_status = "dealed"
        alarm.deal_desc = desc
        alarm.saveEx()

        return result

    def list_alarm_by_aptm_or_agw_id(self, aptm_id="", agw_id="", pager={}):
        """
        根据房间ID或设备UID，查询报警列表
        :param aptm_id:T-string, 房间ID
        :param agw_id:T-string, 网关设备ID
        :param pager:T-object{page_no:#int, page_size:#int}, 分页参数
        :return:data->{}
        """
        result = get_default_result()
        if not aptm_id or not agw_id:
            return result.setmsg("参数错误", 3)

        alarms = AlarmRecord.objects()
        if agw_id:
            alarms = alarms.filter(device=agw_id)

        if aptm_id:
            alarms = alarms.filter(aptm=aptm_id)

        result.data = paginate_query_set(alarms, pager)

        return result

    def list_alarms(self, project_id, phase_no=0, building_no=0, aptm_short_code="", pager={}):
        """
        报警查询
        :param project_id:
        :param phase_no:
        :param building_no:
        :param aptm_short_code:
        :param pager:
        :return:
        """
        result = get_default_result()
        conditions = {"project": project_id}
        codes = [phase_no, building_no, 0, 0, 0]

        if aptm_short_code:
            codes[3:] = tools.parse_aptm_short_code(aptm_short_code)

        aptm_pattern = tools.parse_codes_to_aptm_uuid_pattern(codes)

        conditions.update({"aptm_uuid": re.compile(aptm_pattern)})

        alarms = AlarmRecord.objects(**conditions).order_by("-created_at")
        result.data = paginate_query_set(alarms, pager)
        return result


class RecordApi(BaseApi):
    """报警记录，通知记录Api"""

    def _notice_agw_unbind(self, agw, aptm):
        """
        网关设备解绑通知（push_type=notification）
        :param agw:
        :param aptm:
        :return:
        """
        now = datetime.datetime.now()
        group = "non_aptm"
        aptm_name = ""
        dt_str = "{0}月{1}日 {2:0>2}:{3:0>2}".format(now.month, now.day, now.hour, now.minute)
        if aptm:
            group = str(aptm.id)
            aptm_name = aptm.name

        content = "%s %s解绑报警网关%s" % (dt_str, aptm_name, agw.mac)

        tools.send_push_message(content=content, tags=group, domains=aptm.domain)

    def _notice_agw_bcf(self, bcf, user, area=None, is_from_dev=False):
        """
        布撤布通知
        :param bcf:
        :param user:
        :return:
        """
        now = datetime.datetime.now()
        dt_str = "{0}月{1}日 {2:0>2}:{3:0>2}".format(now.month, now.day, now.hour, now.minute)
        op_name = "批量布防" if bcf.op_enable else "批量撤防"
        aptm = bcf.aptm
        aptm_name = ""
        user_name = "系统"

        if not aptm:
            log.debug("Not found aptm")
            return False

        aptm_name = aptm.name

        def __on_human_op():

            nonlocal user_name, aptm_name, op_name
            alarm_loc_name, alarm_type_name = "", ""

            if user.__class__.__name__ == "QdUser":
                user_name = "用户%s" % (user.name or user.mobile)
                bcf.op_user_id_desc = "%s:%s" % (user.__class__.__name__, user.id)

            elif user.__class__.__name__ == "WueyUser":
                user_name = "物业"
                bcf.op_user_id_desc = "%s:%s" % (user.__class__.__name__, user.id)

            if area:
                op_name = "布防" if bcf.op_enable else "撤防"
                alarm_type_name = misc.Alarm_Types_ZH.get(area.alarm_type, "") + "报警器"
                alarm_loc_name = area.loc_name

            bcf.name = "%s %s对%s%s%s进行%s" % (dt_str, user_name, aptm_name, alarm_loc_name, alarm_type_name, op_name)

        # End def _on_human_op

        if is_from_dev:  # 按键操作
            bcf.name = "%s %s操作按键%s" % (dt_str, aptm_name, op_name)

        if not is_from_dev and user:  # 人为操作
            __on_human_op()

        bcf.saveEx()

        # 发送通知
        extras = {"msg_type": misc.NoticeTypesEnum.bcf, "msg_data": bcf.outputEx()}
        tools.send_push_message(content=bcf.name, extras=extras, tags=str(aptm.id), domains=aptm.domain)

        return True

    @classmethod
    def _create_agw_offline_notice(cls, dev):
        """
        创建网关离线通知
        :param dev:
        :return:
        """
        now = datetime.datetime.now()
        dt_str = "{0}月{1}日 {2:0>2}:{3:0>2}".format(now.month, now.day, now.hour, now.minute)
        offline = AgwOffLineNotice(project=dev.project, aptm=dev.aptm, device=dev, domain=dev.domain)

        aptm = dev.aptm
        aptm_name = aptm.get_aptm_full_name()
        offline.name = "%s %s报警网关离线" % (dt_str, aptm_name)

        offline.saveEx()

        return offline

    @app_user_login_required
    @rds_api_cache(ex=20, think_session=False)
    def get_all_last_records(self, agw_id, max=500):
        """
        获取最近一周的记录（包括报警,操作设备，设备离线）
        按时间排序后，最多返回max条数据
        :param agw_id: T-string|list, 网关设备ID,或网关设备ID列表
        :param max: T-int, 最大数据行
        :return: data->{collection:[{id:#str, name:#str, created_at:#int, ...}]}
        """

        result = get_default_result()
        before = datetime.datetime.now() + datetime.timedelta(days=-7)

        _collection = []
        result.data_collection = []
        if not agw_id:
            return result

        agw_id_list = []
        
        if isinstance(agw_id, str):
            agw_id_list = [agw_id]
        else:
            agw_id_list = agw_id

        alarms = AlarmRecord.objects(device__in=agw_id_list, created_at__gt=before).order_by("-created_at")[:max]
        # warnings = WarningRecord.objects(device__in=agw_id_list, created_at__gt=before).order_by("-created_at")[:max]
        offline_notices = AgwOffLineNotice.objects(device__in=agw_id_list, created_at__gt=before).order_by("-created_at")[:max]
        bcf_notices = AgwBcfNotice.objects(device__in=agw_id_list, created_at__gt=before).order_by("-created_at")[:max]

        for o in alarms: _collection.append(o)
        # for o in warnings: _collection.append(o)
        for o in offline_notices: _collection.append(o)
        for o in bcf_notices: _collection.append(o)

        _collection.sort(key=lambda o: o.created_at, reverse=-1)

        for o in _collection:
            _cls = o.__class__.__name__
            _o = dict(id=str(o.id), name=o.name, created_at=o.created_at.timestamp() * 1000, _cls=_cls)
            if _cls == AlarmRecord.__name__:
                _o['alarm_type'] = o.alarm_type
                _o['deal_status'] = o.deal_status

            elif _cls == WarningRecord.__name__:
                _o['alarm_type'] = o.alarm_type

            result.data_collection.append(_o)

        return result

    @common_login_required
    def aio_sync_alarm_records(self, sync_timestamp=0):
        """
        物业机同步报警记录
        :param sync_timestamp: T-int,上次同步时间截(秒)
        :return: data->{collection:[...], sync_timestamp:#int}
        """
        result = get_default_result()
        now = datetime.datetime.now()
        dev = self._get_login_device()

        result.data_collection = []

        if not dev:
            return result.setmsg("Not found device.", 3)

        result.setdata("sync_timestamp", int(now.timestamp()))
        before = now - datetime.timedelta(days=30)
        if sync_timestamp: before = datetime.datetime.fromtimestamp(sync_timestamp)

        alarms = AlarmRecord.objects(project=dev.project, created_at__gte=before)
        result.data_collection_output(alarms)

        return result

    @common_login_required
    def aio_deal_alarm(self, alarm_id, deal_status="dealed", deal_desc="", wy_user_id=""):
        """
        物业机 处理报警 填写备注信息
        :param alarm_id: T-str, 报警ID
        :param deal_status: T-str, 处理状态 dealed | undealed
        :param deal_desc: T-str, 处理备注信息
        :param wy_user_id: T-str, 物业处理人ID
        :return: data->{}
        """
        result = get_default_result()
        dev = self._get_login_device()
        alarm = AlarmRecord.objects(project=dev.project, id=alarm_id).first()

        if not alarm:
            return result.setmsg("操作失败", 3)

        if deal_status not in ["dealed", "undealed"]: deal_status = "dealed"
        
        alarm.deal_status = deal_status
        if deal_desc: alarm.deal_desc = deal_desc

        alarm.saveEx()
        return result.setmsg("操作完成")
