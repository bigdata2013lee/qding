# coding=utf-8
import datetime
import json
import logging
import queue
import re
import threading

import time

from utils import qd
from utils import tools
from utils import misc
from utils.misc import NoticeTypesEnum
from utils.qd import QdRds

log = logging.getLogger("qdcommevts")
process_exception_exit, reg_signal_term, is_stop_status, process_exit_status = tools.mk_process_crt(log=log)
task_queue_name = 'qdcommevts_task_queue'
rds = QdRds.get_redis()

stt_rds = QdRds.get_statictic_redis()
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
    @care_etype("missed_call")
    def do_missed_call(cls, qdevt):
        from models.aptm import Room
        aptm_id = qdevt.data.get("aptm", "")
        to_desc = qdevt.data.get("to_desc", "")

        if not aptm_id: return

        aptm = Room.objects(id=aptm_id).first()

        now = datetime.datetime.now()
        dt_str = "{0}月{1}日 {2:0>2}:{3:0>2}".format(now.month, now.day, now.hour, now.minute)

        content = "%s %s 有一个来自门口机未接来电" % (dt_str, to_desc)
        extras = {"msg_type": misc.NoticeTypesEnum.missed_call, "msg_data": {}}
        tools.send_push_message(content=content, tags=aptm_id, extras=extras, domains=aptm.domain)

    @classmethod
    @care_etype("device_heartbeat_status_change")
    def do_dhsc_for_stt(cls, qdevt):
        """agw/gate/aio 心跳状态变化时，跟踪在线数量"""
        log.debug("device_heartbeat_status_change: evt data -> %s", qdevt.data)
        dev_type = qdevt.data.get("dev_type", "")
        project_id = qdevt.data.get('dev', {}).get("project", "")
        status = qdevt.data.get("status", "up")

        if not dev_type or not project_id:
            log.warning('Not found "dev_tpe:%s" or "project_id:%s" in qdevt.', dev_type, project_id)
            return

        stt_rds.hincrby("%s_onlines" % dev_type, project_id, 1 if status == 'up' else -1)

    @classmethod
    @care_etype("trigger_agw_alarm")
    def clear_api_cache_for_agw_alarm(cls, qdevt):
        """触发报警时，清除项目有关的api方法缓存"""
        project_id = qdevt.project_id
        QdRds.delete_api_cache_key("StatisticApi.stt_alarm_categorys", mgr_key=project_id)
        QdRds.delete_api_cache_key("StatisticApi.get_last_alarms", mgr_key=project_id)

    @classmethod
    @care_etype("trigger_agw_alarm")
    def send_agw_alarm_to_app(cls, qdevt):
        """触发报警时，发送通知到app"""
        Enum = misc.NoticeTypesEnum
        alarm_json = qdevt.data
        extras = {"msg_type": Enum.alarm, "msg_data": alarm_json}
        tools.send_push_message(content=alarm_json.get("name", ""), extras=extras, tags=alarm_json.get("aptm", ""),
                                domains=alarm_json.get("domain", ""))

    @classmethod
    @care_etype("trigger_agw_alarm")
    def send_agw_alarm_to_app(cls, qdevt):
        """触发报警时，发送通知到物业机"""
        Enum = misc.NoticeTypesEnum
        alarm_json = qdevt.data
        extras = {"msg_type": Enum.alarm, "msg_data": alarm_json}
        tools.send_push_message(content=alarm_json.get("name", ""), extras=extras, tags=alarm_json.get("project", ""))


    @classmethod
    @care_etype("trigger_agw_warning")
    def send_agw_alarm_to_app(cls, qdevt):
        """触发警告时，发送通知到app"""
        Enum = misc.NoticeTypesEnum
        warning_json = qdevt.data
        extras = {"msg_type": Enum.delay_alarm, "msg_data": warning_json}
        tools.send_push_message(content=warning_json.get("name", ""), extras=extras, tags=warning_json.get("aptm", ""),
                                domains=warning_json.get("domain", ""))

    @classmethod
    @care_etype("login_by_mobile_verfi_code")
    def notice_app_user_login(cls, qdevt):
        """App用户登陆时，发jpush通知"""
        user_id = qdevt.data.get("app_user_id", "")
        if not user_id: return

        md5_login_token = tools.md5_str(qdevt.data.get("login_token", ""))

        log.debug("notice_app_user_login -> user_id:%s, login_token:%s, md5_login_token:%s", user_id,
                  qdevt.data.get("login_token", ""), md5_login_token)

        extras = dict(msg_type=NoticeTypesEnum.app_user_logined, msg_data={"md5_login_token": md5_login_token})
        tools.send_push_message(content="", extras=extras, alias=[user_id])


@process_exception_exit
def listen_qdevents():
    ps = rds.pubsub(ignore_subscribe_messages=True)
    ps.psubscribe("QDEventOn:*")  # 增加*args参数以扩展新的模式

    def __pubsub_message_handler(message):
        log.debug(message)
        evt_id = message.get("data", b'').decode('utf-8')
        if not evt_id: return

        qdevt = qd.QDEvent.get_event(evt_id)
        log.debug("revc qdevt: %s" % qdevt)
        if not qdevt: return

        # 设置一个处理标记位(并检查)，用于分布式程序的协同
        if not QdRds.nx("nx_qdcommevts_task_queue_already_append_qdevt_%s" % evt_id): return
        rds.lpush(task_queue_name, evt_id)

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
                _task = rds.rpop(task_queue_name)
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
    run_threads(thead_count=10, depend_ths=[evt_listen_th])
    process_exit_status()
