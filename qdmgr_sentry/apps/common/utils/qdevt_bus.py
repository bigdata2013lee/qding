# coding=utf-8
import logging
import time,threading

from utils.qdevt import QdEventBus

log = logging.getLogger('qdevt_bus')


def _run_task_threads(task_fun, thead_count=2, depend_ths=[]):
    """
    多线程执行某个任务
    :param task_fun:
    :param thead_count:
    :param depend_ths:
    """
    threads = []

    for th in depend_ths:
        threads.append(th)
        th.start()

    for num in range(0, thead_count):
        t = threading.Thread(target=task_fun)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
        

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
    _run_task_threads(task_fun, thead_count=1, depend_ths=[dt1])

