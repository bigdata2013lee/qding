# coding=utf-8
import base64
import json
import logging
import os
import time
import redis
import requests

from redis.sentinel import Sentinel

from conf.qd_conf import CONF
from models.common import Sysconfig

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
        self['data'][key] = val
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

    @classmethod
    def getrange(cls, file_id, start, end):
        rds = QdRds.get_file_cache_redis()
        file_id = "%s" % file_id
        buf = rds.getrange(file_id, start, end-1)
        return buf


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


class CWFaceApiTool(object):

    @classmethod
    def call_face_server(cls, url, **kwargs):
        url = "http://10.39.249.60:8000/%s?app_id=user&app_secret=12345" % url

        headers = {
            'user-agent': 'python-client',
            'Accept-Encoding': ', '.join(('gzip', 'deflate')),
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }

        session = requests.Session()

        post_params = {}

        post_params.update(kwargs)
        response = session.request('POST', url, data=post_params, timeout=4, headers=headers, stream=True)
        res_data = response.content.decode("utf-8")
        log.debug(res_data)
        return json.loads(res_data)

    @classmethod
    def detect(cls, img_base64, mode=False):
        params = {"img": img_base64}
        if mode: params['mode'] = 'true'

        call_res = cls.call_face_server("face/tool/detect", **params)
        return call_res


class FileStorage(object):
    @classmethod
    def save_file(cls, file_content, file_path):
        with open(file_path, "wb+") as my_file:
            my_file.write(file_content)

    @classmethod
    def save_image(cls, img_base64, base_dir="family", sync=False):
        """
        :param img_base64:
        :param base_dir: T-str, chioces [family, public]
        :return:
        """
        from utils import tools
        from utils.tasks import sync as _s, Tasks
        img_bytes = base64.standard_b64decode(img_base64)
        img_path = "%s/%s.jpg" % (base_dir, tools.get_uuid())
        _img_path = os.path.join(CONF['app_home'], "temp", img_path)
        if not sync:
            cls.save_file(img_bytes, _img_path)
        else:
            _s(Tasks.save_file, img_bytes, _img_path)
        return img_path


class MQTTMessageTool(object):
    @classmethod
    def wait_reply(cls, msg_id, time_out):
        time_base = time.time()
        msg_reply = None
        _rds = QdRds.get_redis()
        while not msg_reply:
            msg_reply = _rds.get(msg_id)
            if msg_reply:
                break
            if time.time() - time_base >= time_out:
                return None

            time.sleep(0.05)
        msg_str = (msg_reply or b'{}').decode("utf-8")
        msg_reply = json.loads(msg_str)
        _rds.delete(msg_id)

        return msg_reply

    @classmethod
    def create_msg(cls, msg_type, msg_title='', msg_data={}):
        from utils import tools
        msg_id = 'msgid_{0}'.format(tools.get_uuid())
        message = {'msg_id': msg_id, 'msg_type': msg_type,
                   'msg_title': msg_title, 'msg_data': msg_data}

        return message

    @classmethod
    def send_message(cls, topic, msg={}):
        _rds = QdRds.get_redis()

        _rds.lpush("mqtt_push", json.dumps(dict(topic=topic, extras=msg)))


class SysconfigTool(object):
    @classmethod
    def sys_config(cls, name, options=None):
        """Get/Set 系统配置选项"""
        if not name:
            raise Exception("sys_config func argument error.")

        if options is not None and not isinstance(options, dict):
            raise Exception("sys_config func argument error.")

        sc = Sysconfig.objects(name=name).first()

        # get
        if options is None:
            if not sc: return {}
            return sc.options

        # set
        if not sc:
            sc = Sysconfig(name=name)
            sc.save()

        sc.options.update(options)
        sc.save()

    @classmethod
    def list_names(cls):
        return [sc.name for sc in Sysconfig.objects()]

    @classmethod
    def remove(cls, name):
        Sysconfig.objects(name=name).delete()