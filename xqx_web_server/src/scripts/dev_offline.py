# coding=utf-8

import time
import threading
import re

import pickle

from models.device import Gate, AioManager
from utils import qd
from utils import tools
import logging

from utils.qd import QdRds

log = logging.getLogger("dev_offline")


__doc__ = """
检查 门口机\物业机 设备离线
"""
process_exception_exit, reg_signal_term, is_stop_status, process_exit_status = tools.mk_process_crt(log=log)
task_queue_name = 'dev_offline_task_queue'
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

        find = re.findall("(gate|aio)_heartbeat_([0-9a-f]{24})", expired_key)
        if not find: return

        dev_type = find[0][0]
        dev_id = find[0][1] if find else ""

        # 设置一个处理标记位(并检查)，用于分布式程序的协同
        if not QdRds.nx("nx_dev_offline_task_queue_already_append_%s_%s" % (dev_type, dev_id)): return
        rds.lpush(task_queue_name, pickle.dumps((dev_type, dev_id)))

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


def deal_dev_offline(dev_type, dev_id):
    """
    处理离线任务
    1.更新设备心跳状态
    2.记录并发送离线通知
    :param dev_type: T-string, 类型 gate|aio
    :param dev_id: T-string, 设备ID
    :return:
    """
    dev = None
    if dev_type == 'gate': dev = Gate.objects(id=dev_id).first()
    elif dev_type == 'aio': AioManager.objects(id=dev_id).first()

    if not dev: return False

    ostatus = dev.heartbeat.get("status", "up")
    dev.update(__raw__={"$set": {"heartbeat.status": "down"}})

    if ostatus != 'down':
        evt_data=dict(dev=dev.outputEx(), status='down', dev_type=dev.__class__.__name__)
        qd.QDEvent("device_heartbeat_status_change", data=evt_data).broadcast()

    return True


def run_threads(thead_count=2, depend_ths=[]):

    def _do_task():
        while True:
            if is_stop_status():return
            task = ("", "")
            try:
                _task = rds.rpop(task_queue_name)
                if _task: task = pickle.loads(_task)
            except Exception as e:
                log.exception(e)
                time.sleep(2)  # 最大的可能是redis连接断开，在此暂停2s
                continue

            if not task or not task[0] or not task[1]:
                time.sleep(1)
                continue

            try:
                dev_type, dev_id = task
                deal_dev_offline(dev_type, dev_id)

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
    run_threads(thead_count=8, depend_ths=[evt_listen_th])
    log.debug("process over")
    process_exit_status()

