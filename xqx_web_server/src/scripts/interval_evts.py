# coding=utf-8
import datetime
import logging
import threading

import time

from models.aptm import Project
from models.device import Gate, AioManager, AlarmGateway
from utils import qd
from utils import tools
from utils.qd import QdRds

__doc__ = """
间隔定时任务执行进程
依赖 interval_evt_trigger进程
"""

log = logging.getLogger("intervalevts")
process_exception_exit, reg_signal_term, is_stop_status, process_exit_status = tools.mk_process_crt(log=log)
task_queue_name = 'intervalevts_task_queue'

comm_rds = QdRds.get_redis()


def care_etype(evt_name):
    def _d1(func):
        if not getattr(care_etype, "qd_evt_names", None):care_etype.qd_evt_names = {}
        methods = care_etype.qd_evt_names.get(evt_name, None)
        if methods is None: care_etype.qd_evt_names[evt_name] = []

        care_etype.qd_evt_names[evt_name].append(func)

        def _d2(*args, **kwargs):
            res = func(*args, **kwargs)
            return res

        return _d2

    return _d1


class EvtHandler(object):

    @classmethod
    @care_etype("interval_evt_trigger_60_minute")
    def refix_device_onlines(cls, qdevt):
        """
        重新修正各项目设备在线个数的统计
        :param qdevt:
        """
        log.debug(">>refix_device_onlines")
        from apis.statistic import StatisticApi

        stt_api = StatisticApi()
        for project in Project.objects():
            stt_api.refix_device_onlines(project_id=project.id, select="")


    @classmethod
    @care_etype("interval_evt_trigger_8_hour")
    def fix_aio_gate_offline(cls, qdevt):
        """
        修正 管理机、门口机 离线状态
        """

        log.debug(">>fix_aio_gate_offline")

        before = datetime.datetime.now() - datetime.timedelta(minutes=30)

        gates = Gate.objects(heartbeat__at__lte=before, heartbeat__status="up")
        gates.update(__raw__={"$set": {"heartbeat.status": "down"}})

        aios = AioManager.objects(heartbeat__at__lte=before, heartbeat__status="up")
        aios.update(__raw__={"$set": {"heartbeat.status": "down"}})

    @classmethod
    @care_etype("interval_evt_trigger_12_hour")
    def fix_agw_offline(cls, qdevt):
        """
        修正 网关设备 离线状态
        """
        log.debug(">>fix_agw_offline")
        before = datetime.datetime.now() - datetime.timedelta(minutes=30)
        agws = AlarmGateway.objects(heartbeat__at__lte=before, heartbeat__status="up")
        agws.update(__raw__={"$set": {"heartbeat.status": "down"}})


@process_exception_exit
def listen_qdevents():
    ps = comm_rds.pubsub(ignore_subscribe_messages=True)
    ps.psubscribe("QDEventOn:interval_evt_trigger_*_minute", "QDEventOn:interval_evt_trigger_*_hour")  # 增加*args参数以扩展新的模式

    def __pubsub_message_handler(message):
        evt_id = message.get("data", b'').decode('utf-8')
        if not evt_id: return

        qdevt = qd.QDEvent.get_event(evt_id)
        log.debug("revc qdevt: %s" % qdevt)
        if not qdevt: return

        # 设置一个处理标记位(并检查)，用于分布式程序的协同
        if not QdRds.nx("nx_intervalevts_task_queue_already_append_qdevt_%s" % evt_id): return
        comm_rds.lpush(task_queue_name, evt_id)

    while True:
        if is_stop_status(): return
        try:
            m = ps.get_message()
            if not m: continue
            __pubsub_message_handler(m)

        except Exception as e:
            log.exception(e)
            time.sleep(3)

        time.sleep(0.05)


def deal_qdevt(evt):
    """
    事件处理
    """
    log.debug("etype:%s", evt.etype)
    methods = care_etype.qd_evt_names.get(evt.etype, [])
    if not methods:
        log.warn("不支持的事件类型%s", evt.etype)
        return False

    log.debug(methods)
    for m in methods:
        try:
            m(EvtHandler, evt)
        except Exception as e:
            log.exception(e)

    return True


def run_threads(thead_count=2, depend_ths=[]):

    def _do_task():
        while True:
            if is_stop_status(): return
            task = ""
            try:
                _task = comm_rds.rpop(task_queue_name)
                if _task: task = _task.decode("utf-8")
            except Exception as e:
                log.exception(e)
                time.sleep(2)
                continue

            if not task:
                time.sleep(1)
                continue

            try:
                evt = qd.QDEvent.get_event(task)
                deal_qdevt(evt)
            except Exception as e:
                log.exception(e)

    threads = []

    for th in depend_ths:
        threads.append(th)
        th.start()

    for num in range(0, thead_count):
        t = threading.Thread(target=_do_task)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


def run():
    reg_signal_term()
    evt_listen_th = threading.Thread(target=listen_qdevents)
    run_threads(thead_count=4, depend_ths=[evt_listen_th])
    process_exit_status()
