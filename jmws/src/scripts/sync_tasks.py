# coding=utf-8
import logging
import time
import pickle

from utils.qd import QdRds
from utils.tasks import Tasks  # can't del
from utils.tools import run_task_threads

log = logging.getLogger('sync_tasks')


rds = QdRds.get_redis()


def loop_tasks():

    def __get_serialize_task():

        try:
            _serialize_task = rds.rpop("sync_tasks")
            if not _serialize_task: return None
            serialize_task = pickle.loads(_serialize_task)

            return serialize_task

        except Exception as e:
            log.exception(e)
            return None

    while True:

        serialize_task = __get_serialize_task()

        if not serialize_task:
            time.sleep(1)
            continue

        log.debug(serialize_task)
        method_name = serialize_task.get("method_name", 'non_func')
        method = getattr(Tasks, method_name, None)
        if not method: continue

        args = serialize_task.get("args", [])
        kwargs = serialize_task.get("kwargs", {})

        try:
            method(*args, **kwargs)

        except Exception as e:
            log.exception(e)


def run():
    run_task_threads(loop_tasks, thead_count=20)

