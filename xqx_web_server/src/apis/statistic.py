#coding=utf-8
import datetime
import logging

import itertools

from apis.base import BaseApi
from models.aptm import Project
from models.device import Gate, AioManager, AlarmGateway
from models.record import AlarmRecord
from utils import tools
from utils.qd import QdRds
from utils.tools import get_default_result, rds_api_cache

log = logging.getLogger('django')
stt_rds = QdRds.get_statictic_redis()


class StatisticApi(BaseApi):
    """
    提供统计分析及首页概要功能
    """

    @rds_api_cache(60, think_session=False)
    def _stt_all_gates(self, project_id, gate_type="UnitGate"):

        devs = Gate.objects(project=project_id, is_valid=True, _cls="Gate.%s" % gate_type)
        return devs.count()

    def stt_gate_onlines(self, project_id, gate_type="UnitGate"):
        """
        统计在线门口机的个数，包括了设备总数
        :param project_id:
        :return: data->{online:#int, all:#int}
        """
        result = get_default_result()
        count = stt_rds.hget("%s_onlines" % gate_type, project_id) or 0
        result.data = dict(online=int(count), all=self._stt_all_gates(project_id, gate_type=gate_type))
        return result

    @rds_api_cache(60, think_session=False)
    def _stt_all_aios(self, project_id):

        devs = AioManager.objects(project=project_id, is_valid=True)
        return devs.count()

    def stt_aio_onlines(self, project_id):
        """
        统计在线管理机的个数，包括了设备总数
        :param project_id:
        :return: data->{online:#int, all:#int}
        """
        result = get_default_result()
        count = stt_rds.hget("%s_onlines" % AioManager.__name__, project_id) or 0
        result.data = dict(online=int(count), all=self._stt_all_aios(project_id))
        return result

    @rds_api_cache(60, think_session=False)
    def _stt_all_agws(self, project_id):

        devs = AlarmGateway.objects(project=project_id, is_valid=True)
        return devs.count()

    def stt_agw_onlines(self, project_id):
        """
        统计在线报警网关的个数，包括了设备总数
        :param project_id:
        :return: data->{online:#int, all:#int}
        """
        result = get_default_result()
        count = stt_rds.hget("%s_onlines" % AlarmGateway.__name__, project_id) or 0
        result.data = dict(online=int(count), all=self._stt_all_agws(project_id))
        return result

    @rds_api_cache(90, think_session=False)
    def refix_device_onlines(self, project_id, select=""):
        """
        针对某个项目，复位所有设备在线个数
        :param project_id: T-str, 项目ID
        :param select: T-str, 选择类型 "" | "comm" | "agw"
        :return:
        """
        result = get_default_result()
        if not project_id or not Project.objects(id=project_id).first():
            return result.setmsg("未找到相应的社区项目", 3)

        if select in ["", "comm"]:
            # refix aio
            devs = AioManager.objects(project=project_id, is_valid=True, heartbeat__status='up')
            count = devs.count()
            stt_rds.hset("%s_onlines" % AioManager.__name__, project_id, count)

            # refix UnitGate
            devs = Gate.objects(project=project_id, is_valid=True, heartbeat__status='up', _cls="Gate.UnitGate")
            count = devs.count()
            stt_rds.hset("UnitGate_onlines", project_id, count)

            # refix FenceGate
            devs = Gate.objects(project=project_id, is_valid=True, heartbeat__status='up', _cls="Gate.FenceGate")
            count = devs.count()
            stt_rds.hset("FenceGate_onlines", project_id, count)

        if select in ["", "agw"]:
            # refix agw
            devs = AlarmGateway.objects(project=project_id, is_valid=True, heartbeat__status='up')
            count = devs.count()
            stt_rds.hset("%s_onlines" % AlarmGateway.__name__, project_id, count)

        return result

    @rds_api_cache(60, think_session=False)
    def get_last_offline_gates(self, project_id):
        """
        获取最近离线的门口机列表
        :param project_id:
        :return:
        """
        result = get_default_result()
        conditions = dict(project=project_id, is_valid=True, heartbeat__status='down')
        devs = Gate.objects(**conditions).order_by("-heartbeat__at")[:12]
        result.data_collection = [dev.outputEx() for dev in devs]
        return result

    @rds_api_cache(60, think_session=False)
    def get_last_offline_aios(self, project_id):
        """
        获取最近离线的管理机列表
        :param project_id:
        :return:
        """
        result = get_default_result()
        conditions = dict(project=project_id, is_valid=True, heartbeat__status='down')
        devs = AioManager.objects(**conditions).order_by("-heartbeat__at")[:12]
        result.data_collection = [dev.outputEx() for dev in devs]
        return result

    @rds_api_cache(30, think_session=False)
    def get_last_offline_agws(self, project_id):
        """
        获取最近离线的报警网关列表
        :param project_id:
        :return:
        """
        result = get_default_result()
        conditions = dict(project=project_id, is_valid=True, heartbeat__status='down')
        devs = AlarmGateway.objects(**conditions).order_by("-heartbeat__at")[:12]
        result.data_collection = [dev.outputEx(exculde_fields=['alarm_areas']) for dev in devs]
        return result

    @rds_api_cache(3600*24, think_session=False, mgr_key="kwargs.get('project_id','') or args[1]")
    def stt_alarm_categorys(self, project_id):
        """
        分类统计报警记录(最近3天)
        :param project_id:
        :return: data->{stt_categorys:{$alarm_type:[all_count, undealed_count, dealed_count]}}
        """
        result = get_default_result()
        stt_categorys = {}

        before_at = datetime.datetime.now() - datetime.timedelta(hours=24*7)
        conditions = dict(project=project_id, created_at__gte=before_at)
        alarms = AlarmRecord.objects(**conditions).order_by("alarm_type")

        # groupby 前，需要排序
        groups = itertools.groupby(alarms, key=lambda o: o.alarm_type)

        for m, items in groups:
            all_count = len(list(items))
            undealed_count = len(list(filter(lambda x: x.deal_status == "undealed", items)))
            dealed_count = all_count - undealed_count

            stt_categorys[m] = (all_count, undealed_count, dealed_count)

        return result.setdata('stt_categorys', stt_categorys)

    @rds_api_cache(3600*24, think_session=False, mgr_key="kwargs.get('project_id','') or args[1]")
    def get_last_alarms(self, project_id):
        """
        获取最近的报警记录列表
        :param project_id:
        :return:
        """
        result = get_default_result()
        before_at = datetime.datetime.now() - datetime.timedelta(hours=24)
        conditions = dict(project=project_id, created_at__gte=before_at)
        alarms = AlarmRecord.objects(**conditions).order_by("-created_at")[:12]
        result.data_collection = [alarm.outputEx() for alarm in alarms]
        return result

    def stt_all_device_onlines(self, project_id):
        """
        统计所有设备的在线情况
        :param project_id:
        :return: data->{"AioManager":{"online":1, "all":2}}
        """
        result = get_default_result()
        result.data['AioManager'] = self.stt_aio_onlines(project_id).data
        result.data['AlarmGateway'] = self.stt_agw_onlines(project_id).data
        result.data['UnitGate'] = self.stt_gate_onlines(project_id, gate_type="UnitGate").data
        result.data['FenceGate'] = self.stt_gate_onlines(project_id, gate_type="FenceGate").data
        return result







