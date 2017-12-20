# coding=utf-8
import logging
import pickle
log = logging.getLogger('sync_tasks')


def sync(func, *args, **kwargs):
    from utils.qd import QdRds
    rds = QdRds.get_redis()
    params = dict(method_name=func.__name__, args=args, kwargs=kwargs)
    serialize_task = pickle.dumps(params)

    rds.lpush("sync_tasks", serialize_task)


class Tasks(object):

    @staticmethod
    def save_file(file_content, file_path):
        from utils.qd import FileStorage
        FileStorage.save_file(file_content, file_path)

    @staticmethod
    def hello(name):
        log.debug("Hello %s", name)



