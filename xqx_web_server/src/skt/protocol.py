#coding=utf-8

import asyncio

import time

from apis.agw import AGWDeviceApi, AlarmApi, AGWDeviceQueryApi
from apis.upgrade import AgwUpgradeApi
from . import struct_def as sd
import logging

from utils import misc

log = logging.getLogger("skt")


def mark_handeler_topic(num):

    def _d1(func):
        mark_handeler_topic.methods[num] = func
        def _d2(*args, **kwargs):
            res = func(*args, **kwargs)
            return res
        return _d2
    return _d1

mark_handeler_topic.methods = {}


class AlarmGatewayActionHandler(object):
    """
    报警网关业务处理处理器
    每个Handler方法处理完业务返回2种结果bytes或None
    """

    def __init__(self, protocol):
        self.protocol = protocol

    @mark_handeler_topic(2)
    def pull_settings(self, data_rs):
        """
        设备同步(get)布撤防状态, 解绑状态
        :param data_rs:
        """
        log.debug("[pull_settings]")
        packet_head = data_rs.get("packet_head", None)
        payload_list = data_rs.get("payload_list", [])
        if not packet_head or not payload_list:
            log.warning("Not packet_head or payload_list in data result.")
            return None

        net = "Wi-Fi" if packet_head.net == 1 else "GSM"
        dev_info = payload_list[0]

        agw_dev_query_api = AGWDeviceQueryApi()
        upgrade_api = AgwUpgradeApi()
        agw_dev_api = AGWDeviceApi()

        agw_dev_api._heartbeat(dev_info.uid, net=net, mac=dev_info.mac,
                               sw_version=dev_info.sw_version, hw_version=dev_info.hw_version,
                               res_version=dev_info.res_version)
        if not dev_info.uid or not dev_info.mac:
            log.warning("device not uid or mac")
            return None

        sync_infos = agw_dev_query_api._sync_agw_infos_for_dev(dev_uid=dev_info.uid)
        upgrade_files = upgrade_api._get_release_bin_files()

        # 布防信息payloads
        payloads = []
        for bu_fang in sync_infos.get("bu_fang_list", []):
            payload = sd.PayloadBuFang._make(bu_fang)
            payloads.append(payload)

        # 最新版本信息
        if upgrade_files:
            for uf in upgrade_files:
                payload = sd.PayloadFileInfo._make(uf)
                payloads.append(payload)

        # 加一个空的解绑头，没有数据
        un_register_data_item_head_bytes = b''
        if not sync_infos.get("is_bind_aptm", False):
            log.info("%s, %s is_bind_aptm:False", dev_info.mac, dev_info.uid)
            un_register_data_item_head = sd.DataItemHead._make([10, 2, 0])
            un_register_data_item_head_bytes = un_register_data_item_head.parse2bytes()

        log.debug("un_register_data_item_head_bytes:%s", un_register_data_item_head_bytes)
        respone_bytes = sd.DataParser.parse2bytes(2, payloads, ex_bytes=un_register_data_item_head_bytes)

        return respone_bytes

    @mark_handeler_topic(8)
    def push_device_config(self, data_rs):
        """
        设备上传布撤防状态(post) confing device
        从此过程中实现设备的绑定，初始化，自动解绑定其它设备,参考 "AGWDeviceApi._create_update_dev"
        :param data_rs:
        """
        log.debug("[push_device_config]")
        packet_head = data_rs.get("packet_head", None)
        payload_list = data_rs.get("payload_list", [])
        if not packet_head or not payload_list:
            log.warning("Not packet_head or payload_list in data result.")
            return None

        dev_info = payload_list[0]

        # 应该从dev_info中获取
        mac = dev_info.mac

        fang_qu_list = []
        bu_fang_list = []
        alarm_areas = []

        for payload in payload_list:
            if payload._typename == 'PayloadFangQu': fang_qu_list.append(payload)
            elif payload._typename == 'PayloadBuFang': bu_fang_list.append(payload)

        def _map_alarm_area(fang_qu, bu_fang):
            loc_name = misc.Alarm_Locations_ZH.get(fang_qu.addr, "")
            _fq = dict(alarm_id=fang_qu.fq_id, alarm_type=fang_qu.fq_type, loc_name=loc_name, conn_type=fang_qu.trigger_state)
            _bf = dict(enable=bool(bu_fang.enable), delay_alarm_ts=bu_fang.trigger_delay, delay_enable_ts=bu_fang.enable_delay)
            _area = _fq
            _area.update(_bf)
            return _area

        for _area in map(_map_alarm_area, fang_qu_list, bu_fang_list): alarm_areas.append(_area)

        agw_dev_api = AGWDeviceApi()
        fg = agw_dev_api._create_update_dev(dev_info.room, dev_info.uid, mac, alarm_areas=alarm_areas)

        if not fg: return None
        respone_bytes = sd.DataParser.parse2bytes(8)
        return respone_bytes

    @mark_handeler_topic(7)
    def report_bufang(self, data_rs):
        """
        设备上传布撤防状态(post)
        :param data_rs:
        """
        log.debug("[report_bufang]")
        packet_head = data_rs.get("packet_head", None)
        payload_list = data_rs.get("payload_list", [])
        if not packet_head or not payload_list:
            log.warning("Not packet_head or payload_list in data result.")
            return None

        dev_info = payload_list[0]

        bu_fang_list = []
        items = []

        for payload in payload_list:
            if payload._typename == 'PayloadBuFang':
                bu_fang_list.append(payload)

        for bf in bu_fang_list:
            _bf = [bf.fq_id, bool(bf.enable), bf.trigger_delay]
            items.append(_bf)

        agw_dev_api = AGWDeviceApi()
        agw_dev_api._set_agw_alarm_enable_for_dev(dev_info.uid, items=items)

        respone_bytes = sd.DataParser.parse2bytes(7)
        return respone_bytes

    @mark_handeler_topic(3)
    def report_alarm(self, data_rs):
        """
        设备上传报警
        :param data_rs:
        """
        log.debug("[report_alarm]")
        packet_head = data_rs.get("packet_head", None)
        payload_list = data_rs.get("payload_list", [])
        if not packet_head or not payload_list:
            log.warning("Not packet_head or payload_list in data result.")
            return None

        dev_info = payload_list[0]
        alarm_list = payload_list[1:]
        alarm_api = AlarmApi()

        for alarm in alarm_list:
            alarm_api.create_alarm(dev_uid=dev_info.uid, alarm_id=alarm.alarm_id, alarm_type=alarm.alarm_type)

        respone_bytes = sd.DataParser.parse2bytes(3)
        return respone_bytes

    @mark_handeler_topic(9)
    def report_warning(self, data_rs):
        """
        设备上传报警
        :param data_rs:
        """
        log.debug("[report_warning]")
        packet_head = data_rs.get("packet_head", None)
        payload_list = data_rs.get("payload_list", [])
        if not packet_head or not payload_list:
            log.warning("Not packet_head or payload_list in data result.")
            return None

        dev_info = payload_list[0]
        warning_list = payload_list[1:]
        alarm_api = AlarmApi()

        for warning in warning_list:
            alarm_api.create_warning(dev_uid=dev_info.uid, alarm_id=warning.alarm_id, alarm_type=warning.alarm_type)

        respone_bytes = sd.DataParser.parse2bytes(9)
        return respone_bytes

    @mark_handeler_topic(5)
    def download_file(self, data_rs):
        """
        升级文件下载
        :param data_rs:
        """
        log.debug("[download_file]")
        packet_head = data_rs.get("packet_head", None)
        payload_list = data_rs.get("payload_list", [])

        if not packet_head or not payload_list:
            log.warning("Not packet_head or payload_list in data result.")
            return None

        dev_info = payload_list[0]

        data_section_req = payload_list[1] if len(payload_list) >= 2 else None

        if not data_section_req:
            return None

        upgrade_api = AgwUpgradeApi()
        data_section = upgrade_api._request_data_section(data_section_req.fi_id, data_section_req.offset, step=512)

        if not data_section:
            return None

        payloads = []

        payload = sd.PayloadDataSection._make(data_section)
        payloads.append(payload)

        respone_bytes = sd.DataParser.parse2bytes(5, payloads)

        return respone_bytes

    @mark_handeler_topic(10)
    def check_and_update_wifi_info(self, data_rs):
        """
        1.返回最新wifi版本信息
        2.更新本设备的wifi版本号
        :param data_rs:
        """
        log.debug("[check_and_update_wifi_info]")
        packet_head = data_rs.get("packet_head", None)
        payload_list = data_rs.get("payload_list", [])

        if not packet_head or not payload_list:
            log.warning("Not packet_head or payload_list in data result.")
            return None

        if len(payload_list) != 2:
            log.warning("payload_list length must be 2")
            return None

        dev_info = payload_list[0]
        wifi_ver = payload_list[1]

        agw_dev_api = AGWDeviceApi()
        upgrade_api = AgwUpgradeApi()

        agw_dev_api._update_wifi_version(dev_info.uid, wifi_ver.version)
        ver_infos = upgrade_api._get_wifi_last_version_infos()

        if not ver_infos: return None

        payloads = []
        payload = sd.PayloadVerInof._make(ver_infos)
        payloads.append(payload)
        respone_bytes = sd.DataParser.parse2bytes(10, payloads)

        return respone_bytes


class AlarmGatewayProtocol(asyncio.Protocol):

    clients = []

    def __init__(self):
        self.transport = None

    def _write_empty(self):
        self.transport.write(b'')

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        log.debug('Connection from {}'.format(peername))
        self.transport = transport
        transport._last_received_at = int(time.time())
        self.clients.append(transport)

    def error_received(self, exc):
        log.debug('Error received:%s', exc)
        self.transport.close()

    def data_received(self, data):
        """
            接收到客户端的数据，解析数据包，并传入相应的AlarmGatewayActionHandler方法处理

            1. Handler方法应返回bytes或None
            2.遇到 错误 异常 none 时,向客户端回写空byte, transport.write(b'')
            3.正常发完数据后不关闭socket，由Client主动关闭，再由定时任务清理长时间不交互的连接
        """
        self.transport._last_received_at = int(time.time())

        log.debug("data:%s", data)
        result = None
        try:
            result = sd.DataParser.parse(data)
        except Exception as e:
            log.exception(e)
            self._write_empty()
            self.transport.close()
            return

        log.debug("data parse result: %s", result)

        if not result or result.get("err", 0) != 0:
            log.warning("Error in  data result.")
            self._write_empty()
            self.transport.close()
            return

        try:
            m = mark_handeler_topic.methods.get(result["packet_head"].topic)
            rep_bytes = m(AlarmGatewayActionHandler(self), result)

            if rep_bytes:
                log.debug("rep_bytes:%s", rep_bytes)
                self.transport.write(rep_bytes)
            else:
                self._write_empty()

        except Exception as e:
            log.exception(e)
            self._write_empty()

        #self.transport.close()
        return

    def connection_lost(self, exc):
        log.debug('The server/client closed the connection')
        self.transport.close()
        try:
            self.clients.remove(self.transport)
        except Exception as e:
            pass


