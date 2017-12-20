# coding=utf-8

import threading

import time

from utils import tools
from utils import qd
from utils.qd import QdRds


def mks(task_queue_name, subscribes, log):
    evt_handler_cls = None
    rds = QdRds.get_redis()
    process_exception_exit, reg_signal_term, is_stop_status, process_exit_status = tools.mk_process_crt(log=log)


    def set_evt_handler_cls(ehcls):
        nonlocal evt_handler_cls
        evt_handler_cls = ehcls

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


    @process_exception_exit
    def listen_qdevents():
        ps = rds.pubsub(ignore_subscribe_messages=True)
        ps.psubscribe(*subscribes)  # 增加*args参数以扩展新的模式

        def __pubsub_message_handler(message):
            log.debug(message)
            evt_id = message.get("data", b'').decode('utf-8')
            if not evt_id: return

            qdevt = qd.QDEvent.get_event(evt_id)
            log.debug("revc qdevt: %s" % qdevt)
            if not qdevt: return

            # 设置一个处理标记位(并检查)，用于分布式程序的协同
            if not QdRds.nx("nx_%s_already_append_qdevt_%s" % (task_queue_name, evt_id)): return
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
                m(evt_handler_cls, evt)
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

    # # #--------------------------------------------
    return set_evt_handler_cls, care_etype, listen_qdevents, run_threads, reg_signal_term, process_exit_status
