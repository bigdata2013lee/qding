# coding=utf-8
import logging
import threading

import time

from utils import tools
from utils.qdevt import QdEventBus

log = logging.getLogger('qdevt_bus')


def task_fun():
    QdEventBus.listen_qdevents()


def ltrim_qdevt_queues():

    while True:
        time.sleep(2)
        try:
            QdEventBus.ltrim_qdevt_queue()
        except Exception as ex:
            log.exception(ex)

        time.sleep(60)


def run():
    dt1 = threading.Thread(target=ltrim_qdevt_queues)

    # listen_qdevents 只能建立一个线程
    tools.run_task_threads(task_fun, thead_count=1, depend_ths=[dt1])

