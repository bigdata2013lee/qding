# coding=utf-8

import uuid, re, time, pickle
import threading
import functools
import logging

from apps.common.utils.redis_client import rc

log = logging.getLogger('qdevt_bus')
rds = rc.cnn


def _nx(cls, name, ex=60):
    """
    设置一个处理标记位(并检查)，用于分布式程序的协同
    :param name:
    :param ex:
    :return: T-#bool
    """
    return True if rds.set(name, "ok", ex=ex, nx=True) else False

class QDEvent(object):
    """事件，通过Redis广播"""
    def __init__(self, etype, data={}):
        from utils import tools
        self.eid = ("%s" % uuid.uuid4()).replace('-', '')
        self.at = time.time()
        self.etype = etype
        self.data = data

    def broadcast(self, ex=2400):
        val = pickle.dumps(self)
        rds.set("QDEvent:%s" % self.eid, val, ex=ex)
        rds.publish("QDEventOn:%s" % self.etype, self.eid)

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
        :return:
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

        if not handler_cls.handler_name or not handler_cls.etype_patterns:
            ex = Exception("not handler_cls.handler_name or not handler_cls.etype_patterns")
            log.exception(ex)
            raise ex

        log.info("handeler:%s register etype_patterns:%s", handler_cls.handler_name, handler_cls.etype_patterns)
        for etype_pattern in handler_cls.etype_patterns:
            QdEventBus.register_evt(etype_pattern, handler_cls.handler_name)

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
                    evt = QDEvent.get_event(evt_id)  #
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
    evt_count_timer = 0
    evt_subscribe_status = "#"

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
                rds.ltrim(handler_name, 0, 10000*2)
    
    @classmethod
    def dispatche_evt(cls, evt_id, etype_pattern):
        """
        事件分发
        :param evt_id:
        :param etype_pattern:
        """
        channel = "qdevt.pattern:%s" % etype_pattern
        evt_handler_names = rds.smembers(channel)

        for evt_handler_name in evt_handler_names:
            evt_handler_name = evt_handler_name.decode("utf-8")

            # 防止同一事件重复append到一个处理器中
            if not _nx("nx_qdevt.queue_%s_already_%s" % (evt_handler_name, evt_id), ex=20): return
            rds.lpush("qdevt.queue.%s" % evt_handler_name, evt_id)

    @classmethod
    def register_evt(cls, etype_pattern, handler_name):
        """
        事件注册
        :param etype_pattern:
        :param handler_name:
        :return:
        """
        channel = "qdevt.pattern:%s" % etype_pattern

        # 验证handler_name规范
        if not handler_name or not re.findall("^\w{4,100}$", handler_name):
            log.warning("Illegal arguments handler_name:%s", handler_name)
            return

        rds.sadd(channel, handler_name)
        rds.set("qdevt.qdevents_bus_subscribe_status", "%s" % time.time())
        log.info("Handler %s register evt:%s", handler_name, channel)

    @classmethod
    def _get_subscribes(cls):
        qdevt_patterns = rds.keys("qdevt.pattern:*")

        subscribes = [re.sub("qdevt.pattern:", "QDEventOn:", pattern.decode("utf-8")) for pattern in qdevt_patterns]
        return subscribes

    @classmethod
    def _auto_repsubscribe(cls, ps):
        """
        自动重订阅
        以固定周期(10s),查阅事件订阅列表是否发生变化，如果变化则重新订阅
        Redis Key : qdevt.qdevents_bus_subscribe_status 中记录了一个状态值
        :param ps: Redis pubsub object.
        """
        old_evt_count_timer = cls.evt_count_timer
        current_evt_count_timer = time.time()

        # 10 秒周期未到
        if abs(current_evt_count_timer - old_evt_count_timer) < 10:
            return

        cls.evt_count_timer = current_evt_count_timer

        try:
            old_evt_subscribe_status = cls.evt_subscribe_status
            current_evt_subscribe_status = (rds.get("qdevt.qdevents_bus_subscribe_status") or b'').decode("utf-8")

            # 订阅状态未改变
            if current_evt_subscribe_status == old_evt_subscribe_status:
                return

            cls.evt_subscribe_status = current_evt_subscribe_status
            subscribes = cls._get_subscribes() or ["Defalut_values_for_fix_warning"]

            log.info("Auto Repsubscribe:%s", subscribes)
            ps.reset()
            ps.psubscribe(*subscribes)

        except Exception as e:
            log.exception(e)

    @classmethod
    def listen_qdevents(cls):
        """
        事件订阅->侦听->分发
        :return:
        """

        ps = rds.pubsub(ignore_subscribe_messages=True)
        subscribes = cls._get_subscribes() or ["Defalut_values_for_fix_warning"]
        log.info("psubscribe %s at first.", subscribes)
        ps.psubscribe(*subscribes)  # 增加*args参数以扩展新的模式

        def __pubsub_message_handler(message):
            # log.debug(message)
            evt_id = message.get("data", b'').decode('utf-8')
            pattern = message.get("pattern", b'').decode('utf-8')
            if not evt_id or not re.findall("^[0-9a-f]{32}$", evt_id) or not pattern: return

            # 设置一个处理标记位(并检查)，用于分布式程序的协同
            if not _nx("nx_listen_qdevents_bus_evt_id_and_patten_%s_%s" % (evt_id, pattern), ex=20): return

            etype_pattern = re.sub("QDEventOn:", "", pattern)
            cls.dispatche_evt(evt_id, etype_pattern)

        while True:
            try:
                m = ps.get_message()
                cls._auto_repsubscribe(ps)
                if not m:
                    time.sleep(0.5)
                    continue

                __pubsub_message_handler(m)

            except Exception as e:
                log.exception(e)
                time.sleep(3)

            time.sleep(0.05)
