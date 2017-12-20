# coding=utf-8

import time
import logging
import threading

import re
from utils import qd
from utils import tools

from apis.agw import RecordApi
from models.device import AlarmGateway
from utils import misc
from utils.qd import QdRds

log = logging.getLogger("agw_offline")
__doc__ = """
检查网关设备离线
"""
process_exception_exit, reg_signal_term, is_stop_status, process_exit_status = tools.mk_process_crt(log=log)
task_queue_name = 'agw_offline_task_queue'

rds = QdRds.get_redis()


@process_exception_exit
def listen_key_expired_events():
    """
    监听心跳处理服务, 更新数据库设备心跳数据.
    :return:
    """
    log.debug("listen_key_expired_events start")
    ps = rds.pubsub(ignore_subscribe_messages=True)
    ps.subscribe(["__keyevent@1__:expired"])

    def __pubsub_message_handler(message):
        log.debug(message)
        expired_key = message.get("data", b'').decode('utf-8')
        if not expired_key: return

        find = re.findall("agw_heartbeat_([0-9a-f]{24})", expired_key)
        if not find: return

        agw_id = find[0] if find else ""

        log.debug("match agw_id:%s", agw_id)

        # 设置一个处理标记位(并检查)，用于分布式程序的协同
        if not QdRds.nx("nx_agw_offline_task_queue_already_append_agw_%s" % agw_id, ex=20): return
        rds.lpush(task_queue_name, agw_id)

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


def deal_agw_offline(agw_id):
    """
    处理离线任务
    1.更新设备心跳状态
    2.记录并发送离线通知
    :param agw_id: T-string, 报警网关设备ID
    :return:
    """

    dev = AlarmGateway.objects(id=agw_id).first()
    if not dev:
        return False

    ostatus = dev.heartbeat.get("status", "up")
    dev.update(__raw__={"$set": {"heartbeat.status": "down"}})

    if ostatus != 'down':
        evt_data = dict(dev=dev.outputEx(), status='down', dev_type=AlarmGateway.__name__)
        qd.QDEvent("device_heartbeat_status_change", data=evt_data).broadcast()

    # 控制发送离线通知的频率(1小时一次通知)
    if QdRds.nx("nx_notice_agw_offline_in_one_hour_%s" % dev.id, ex=3600):
        offline = RecordApi._create_agw_offline_notice(dev)
        extras = {"msg_type": misc.NoticeTypesEnum.agw_offline, "msg_data": offline.outputEx()}
        tools.send_push_message(content=offline.name, extras=extras, tags="%s" % dev.aptm.id, domains=dev.aptm.domain)

    return True


def run_threads(thead_count=2, depend_ths=[]):

    def _do_task():
        while True:
            if is_stop_status():return
            task = ""
            try:
                _task = rds.rpop(task_queue_name)
                if _task: task = _task.decode("utf-8")
            except Exception as e:
                log.exception(e)
                time.sleep(2)  # 最大的可能是redis连接断开，在此暂停2s
                continue

            if not task:
                time.sleep(1)
                continue

            try:
                deal_agw_offline(task)
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
    evt_listen_th = threading.Thread(target=listen_key_expired_events)
    log.debug("will run_threads")
    run_threads(thead_count=10, depend_ths=[evt_listen_th])
    log.debug("process over")
    process_exit_status()

