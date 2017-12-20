# coding=utf-8
import logging
import re
import time
import threading
import pickle
import functools

from utils.qd import QdRds

log = logging.getLogger('qdevt_bus')

rds = QdRds.get_redis()

evt_q_name = "qdevt_bus_messages"


class QDEvent(object):
    """事件，通过Redis广播"""
    def __init__(self, etype, project_id="", data={}):
        from utils import tools
        self.eid = tools.get_uuid()
        self.etype = etype
        self.at = time.time()
        self.project_id = "%s" % project_id
        self.data = data

    def broadcast(self, ex=2400):
        val = pickle.dumps(self)
        rds.set("QDEvent:%s" % self.eid, val, ex=ex)
        rds.lpush(evt_q_name, "%s:%s" % (self.etype, self.eid))

    @classmethod
    def get_event(cls, eid):

        evt = None
        val = rds.get("QDEvent:%s" % eid)
        if not val: return None

        try:
            evt = pickle.loads(val)
        except Exception as e:
            log.debug(e)

        return evt


class QdEventExecutor(object):
    """
    事件执行、处理器
    运行一个或多个线程，从对应的对列中取出事件ID，并处理这些事件信息
    """
    def __init__(self):
        self.qd_evt_names = {}

    def on(self, evt_name):
        """
        绑定事件
        :param evt_name:
        """

        def _d1(func):
            methods = self.qd_evt_names.get(evt_name, None)
            if methods is None: self.qd_evt_names[evt_name] = []

            self.qd_evt_names[evt_name].append(func)

            @functools.wraps(func)
            def _d2(*args, **kwargs):
                res = func(*args, **kwargs)
                return res

            return _d2

        return _d1

    def bind_handler(self, handler_cls):
        """
        加载事件Handler类型
        :param handler_cls:
        """
        self.evt_handler_cls = handler_cls

        if not handler_cls.handler_name:
            ex = Exception("not handler_cls.handler_name")
            log.exception(ex)
            raise ex

        for evt_name in self.qd_evt_names:
            QdEventBus.register_evt(evt_name, handler_cls.handler_name)

    def deal_qdevt(self, evt):
        """
        事件处理->调用事件绑定的Handler Method
        """
        evt_handler_cls = self.evt_handler_cls

        log.debug("etype:%s, evt_id:%s, handler:%s", evt.etype, evt.eid, evt_handler_cls)
        methods = self.qd_evt_names.get(evt.etype, [])
        if not methods:
            # log.warn("不支持的事件类型%s", evt.etype)
            return False

        for m in methods:
            try:
                m(evt_handler_cls, evt)
            except Exception as e:
                log.exception(e)

        return True

    def run_threads(self, thead_count=2, depend_ths=[]):
        """
        以多线程方法运行
        :param thead_count:
        :param depend_ths:
        """
        _depend_ths = [] + depend_ths

        def _do_task():
            while True:
                evt_id = None
                try:
                    # RPOP 相应的事件队列
                    evt_id = (rds.rpop("qdevt.queue.%s" % self.evt_handler_cls.handler_name) or b'').decode("utf-8")
                except Exception as e:
                    log.exception(e)
                    time.sleep(2)
                    continue

                if not evt_id:
                    time.sleep(1)
                    continue

                try:
                    evt = QDEvent.get_event(evt_id)
                    if not evt:
                        log.debug("Not found QDEvent (%s)", evt_id)
                        continue

                    self.deal_qdevt(evt)
                except Exception as e:
                    log.exception(e)

        threads = []

        for th in _depend_ths:
            threads.append(th)
            th.start()

        for num in range(0, thead_count):
            t = threading.Thread(target=_do_task)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()


class QdEventBus(object):
    """
    事件总线，负责注册、订阅、派发、管理
    """

    @classmethod
    def publish_evt(cls, QDEvent):
        # use QDEvent.broadcast() instead of
        pass

    @classmethod
    def ltrim_qdevt_queue(cls, evt_handler_name="", clear=False):
        """
        事件队列清除功能，防止过多的事件未处理，导致溢出
        :param evt_handler_name: 为空时，清除所有事件队列
        :param clear: 为False时，保留最近2w个消息,否则全部清除
        """
        evt_handler_names = []

        if evt_handler_name:
            evt_handler_names.append("qdevt.queue.%s" % evt_handler_name)
        else:
            evt_handler_names = [k.decode("utf-8") for k in rds.keys("qdevt.queue.*")]

        for handler_name in evt_handler_names:
            if clear:
                rds.ltrim(handler_name, 1, 0)
            else:
                rds.ltrim(handler_name, 0, 10000 * 2)

    @classmethod
    def dispatche_evt(cls, evt_id, etype):
        """
        事件分发
        :param evt_id:
        :param etype:
        """
        channel = "qdevt.pattern:%s" % etype
        evt_handler_names = rds.smembers(channel)

        for evt_handler_name in evt_handler_names:
            evt_handler_name = evt_handler_name.decode("utf-8")

            # 防止同一事件重复append到一个处理器中
            if not QdRds.nx("nx_qdevt.queue_%s_already_%s" % (evt_handler_name, evt_id), ex=12): return
            rds.lpush("qdevt.queue.%s" % evt_handler_name, evt_id)

    @classmethod
    def register_evt(cls, etype, handler_name):
        """
        事件注册, 建立事件与处理器的关系
        :param etype:
        :param handler_name:
        """
        channel = "qdevt.pattern:%s" % etype

        # 验证handler_name规范
        if not handler_name or not re.findall("^\w{4,100}$", handler_name):
            log.warning("Illegal arguments handler_name:%s", handler_name)
            return

        rds.sadd(channel, handler_name)
        log.info("Channel(%s) register handler (%s)", channel, handler_name)

    @classmethod
    def listen_qdevents(cls):
        """
        事件订阅->侦听->分发
        """

        def __pubsub_message_handler(message):
            # log.debug(message)
            evt_id = message.get("evt_id", '')
            evt_type = message.get("evt_type", '')
            if not evt_id or not re.findall("^[0-9a-f]{32}$", evt_id) or not evt_type: return
            cls.dispatche_evt(evt_id, evt_type)

        while True:
            try:
                m_str = rds.rpop(evt_q_name)
                if not m_str:
                    time.sleep(0.5)
                    continue

                find = re.findall("^(.+):(\w+)$", (m_str or b'').decode("utf-8"))

                if not find:
                    time.sleep(0.05)
                    continue

                message = {"evt_type": find[0][0], "evt_id": find[0][1]}
                __pubsub_message_handler(message)

            except Exception as e:
                log.exception(e)
                time.sleep(3)

            time.sleep(0.05)
