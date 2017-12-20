# coding=utf-8
import logging
import pickle
import time
import redis
from redis.sentinel import Sentinel

from conf.qd_conf import CONF

from utils.tools import synchronized

log = logging.getLogger('django')
__doc__ = """
在qd.py中定义一些较大的组件
"""


class ResultDict(dict):

    def setmsg(self, msg="", err=0):
        self['msg'] = msg
        self['err'] = err
        return self

    def setdata(self, key, val):
        self.data[key] = val
        return self

    @property
    def data(self):
        if 'data' not in self: self['data'] = {}
        return self['data']

    @data.setter
    def data(self, data):
        self['data'] = data

    @property
    def data_collection(self):
        if 'data' not in self: self['data'] = {}
        if 'collection' not in self['data']: self['data']['collection'] = []
        return self['data']['collection']

    @data_collection.setter
    def data_collection(self, collection):
        if 'data' not in self: self['data'] = {}
        self['data']['collection'] = collection

    def data_collection_output(self, queryset, *args, **kwargs):
        collection = []
        if 'data' not in self: self['data'] = {}
        self['data']['collection'] = collection
        for o in queryset:
            po = o.outputEx(*args, **kwargs)
            collection.append(po)


class RdsGfsFileCache(object):
    """基于Redis缓存Grid FS 文件"""
    @classmethod
    def set(cls, file, ex=3600):
        if not file: return
        rds = QdRds.get_file_cache_redis()
        file_id = "%s" % file._id
        if rds.exists(file_id):
            rds.expire(file_id, ex)
            return

        while True:
            data = file.read(size=10240)
            if data:
                rds.append(file_id, data)
            else:
                rds.expire(file_id, ex)
                break

    @classmethod
    def get(cls, file_id, buf_size=1024*4):
        rds = QdRds.get_file_cache_redis()
        file_id = "%s" % file_id
        start, end = 0, buf_size - 1

        while True:
            buf = rds.getrange(file_id, start, end)
            if not buf: break
            yield buf
            start += buf_size
            end += buf_size


class DistributedLock(object):
    """
    分布式锁,基于Redis的setNx特性实现
    name 请根据锁定的资源名称制定，不要随意使用相同的名称，避免相同的资源锁名
    """

    def __init__(self, name, timeout=2, ex=10, slp=0.4):
        self.name = "DistributedLock:" + name
        self.trys = timeout
        self.ex = ex
        self.slp = slp
        self.ts = time.time()

    def __enter__(self):
        locked = self._try_lock()
        if not locked: raise Exception("Distributed Lock Timeout.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._release()

    def _try_lock(self):
        """尝试得到锁，超时返回False"""
        rds = QdRds.get_redis()
        while True:
            locked = rds.set(self.name, 1, ex=self.ex, nx=True)
            if locked: return True
            if time.time() - self.ts >= self.trys: return False
            time.sleep(self.slp or 1)

        return False

    def _release(self):
        QdRds.get_redis().delete(self.name)
        return True


class QDEvent(object):
    """事件，通过Redis广播"""
    def __init__(self, etype, eid="", project_id="", data={}):
        from utils import tools
        self.eid = eid or tools.get_uuid()
        self.etype = etype
        self.at = time.time()
        self.project_id = "%s" % project_id
        self.data = data

    def broadcast(self, ex=60):
        rds = QdRds.get_redis()
        val = pickle.dumps(self)
        rds.set("QDEvent:%s" % self.eid, val, ex=ex)
        rds.publish("QDEventOn:%s" % self.etype, self.eid)

    @classmethod
    def get_event(cls, eid):

        evt = None
        rds = QdRds.get_redis()
        val = rds.get("QDEvent:%s" % eid)
        if not val: return None

        try:
            evt = pickle.loads(val)
        except Exception as e:
            log.debug(e)

        return evt


class QdRds(object):

    __comm_redis = None
    __heartbeat_redis = None
    __statictic_redis = None
    __file_cache_redis = None

    @classmethod
    def _select_conn(cls, db=0):
        rds_pattern = CONF.get("redis").get("pattern")

        if rds_pattern == 'sentinel':
            servers = CONF.get("redis").get(rds_pattern).get('servers')
            master_alias = CONF.get("redis").get(rds_pattern).get('master_alias')
            sentinel = Sentinel(servers, socket_timeout=1)
            master = sentinel.master_for(master_alias, db=db)
            return master

        elif rds_pattern == 'single':
            host = CONF.get("redis").get(rds_pattern).get('host')
            port = CONF.get("redis").get(rds_pattern).get('port')
            rds = redis.Redis(host=host, port=port, db=db)
            return rds

        raise Exception("Redis Conf Error.")

    @classmethod
    def delete_api_cache_key(cls, method_name, mgr_key=""):
        rds = cls.get_redis()
        target_key_name = "api_cache_%s%s:*" % (method_name, "\[mgr_key-%s\]" % mgr_key if mgr_key else "")
        keys = rds.keys(target_key_name)
        if not keys: return
        rds.delete(*keys)

    @classmethod
    def get_redis(cls):

        if cls.__comm_redis is not None: return cls.__comm_redis
        rds = cls._select_conn(db=0)
        cls.__comm_redis = rds
        return rds

    @classmethod
    def get_heartbeat_redis(cls):
        if cls.__heartbeat_redis is not None: return cls.__heartbeat_redis
        rds = cls._select_conn(db=1)
        cls.__heartbeat_redis = rds
        return rds

    @classmethod
    def get_statictic_redis(cls):
        if cls.__statictic_redis is not None: return cls.__statictic_redis
        rds = cls._select_conn(db=3)
        cls.__statictic_redis = rds
        return rds

    @classmethod
    def get_file_cache_redis(cls):
        if cls.__file_cache_redis is not None: return cls.__file_cache_redis
        rds = cls._select_conn(db=4)
        cls.__file_cache_redis = rds
        return rds

    @classmethod
    def nx(cls, name, ex=60):
        """
        设置一个处理标记位(并检查)，用于分布式程序的协同
        :param name:
        :param ex:
        :return:
        """
        rds = cls.get_redis()
        return True if rds.set(name, "ok", ex=ex, nx=True) else False

    @classmethod
    def get_auto_ins_num(cls, key_name):
        name = "auto_incr_num_" + key_name
        rds = cls.get_redis()
        val = rds.incr(name, amount=1)
        return val




