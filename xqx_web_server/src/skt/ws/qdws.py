# coding=utf-8
import json
import logging
import queue
import re
import threading

import time

from utils import qd
from utils import tools
from utils.qd import QdRds
from .ws_server import SimpleWebSocketServer, WebSocket

log = logging.getLogger("ws")
rds = QdRds.get_redis()
task_queue = queue.Queue(maxsize=10000)
clients = []
ws_port = 9557
allow_etypes = ['user_application_aptm_bind', 'trigger_agw_alarm']

__doc__ = """

"""

task_queue_name = 'qdws_task_queue'


class SysMsg(WebSocket):

    def handleMessage(self):
        if not isinstance(self.data, (str,)): return
        log.debug("data:%s", self.data)

        try:
            topic_find = re.findall("^topic:(\w+)$", self.data)
            project_find = re.findall("^project:(\w+)$", self.data)

            if topic_find:
                topic = topic_find[0] if topic_find else ""
                self._add_topic(topic)

            elif project_find:

                project = project_find[0] if project_find else ""
                self._add_project(project)
        except Exception as e:
            log.exception(e)

        self.sendMessage("%s"%time.time())

    def handleConnected(self):
        log.debug("%s connected in", self.address)
        self._topics = []
        self._projects = []

        clients.append(self)

    def handleClose(self):
        clients.remove(self)
        log.debug("%s disconnected", self.address)

    def _add_topic(self, topic=""):

        if not topic or topic in self._topics or len(self._topics) > 200:
            return

        self._topics.append(topic)
        return True

    def _add_project(self, project=""):

        if not project or project in self._projects or len(self._projects) > 200:
            return

        self._projects.append(project)
        return True

    @classmethod
    def sendWSMSG(cls, project_id, topic, data={}):

        msg = dict(project_id=project_id, topic=topic, data=data)

        log.debug("msg:%s", msg)

        for client in clients:
            log.debug(client._projects)
            log.debug(client._topics)

            if not (project_id in client._projects and topic in client._topics):
                continue

            log.debug("Send WS Message %s", msg)
            client.sendMessage(json.dumps(msg))


def start_server():
    log.debug("start_server")
    server = SimpleWebSocketServer('', ws_port, SysMsg)
    server.serveforever()


def listen_qdevents():
    ps = rds.pubsub(ignore_subscribe_messages=True)
    ps.psubscribe("QDEventOn:*")  # 增加参数以扩展新的模式

    def __pubsub_message_handler(message):
        log.debug(message)
        evt_id = message.get("data", b'').decode('utf-8')
        if not evt_id: return

        qdevt = qd.QDEvent.get_event(evt_id)
        log.debug("revc qdevt: %s" % qdevt)
        if not qdevt: return

        if qdevt.etype not in allow_etypes: return

        # 设置一个处理标记位(并检查)，用于分布式程序的协同
        if not QdRds.nx("nx_qdws_task_queue_already_append_qdevt_%s" % evt_id): return
        rds.lpush(task_queue_name, evt_id)

    while True:
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
    if evt.etype == 'user_application_aptm_bind':
        SysMsg.sendWSMSG(project_id=evt.project_id, topic=evt.etype, data={})

    elif evt.etype == "trigger_agw_alarm":
        SysMsg.sendWSMSG(project_id=evt.project_id, topic=evt.etype, data=evt.data)

    return True


def run_threads(thead_count=2, depend_ths=[]):

    def _do_task():
        while True:
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


def main():

    log.debug("process start")
    ws_server_th = threading.Thread(target=start_server)
    evt_listen_th = threading.Thread(target=listen_qdevents)
    run_threads(thead_count=4, depend_ths=[ws_server_th, evt_listen_th])

    log.debug("process over")
