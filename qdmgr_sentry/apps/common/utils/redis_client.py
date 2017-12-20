# -*- coding:utf-8 -*-
import redis
import pickle
import logging

from settings.const import CONST

logger = logging.getLogger('qding')


class Redis_Client(object):
    def __init__(self, host=CONST['redis']['host'], port=CONST['redis']['port']):
        self.host = host
        self.port = port
        self.cnn = self.__connect()

    def got(self, dataArea, method='lpop'):
        method = getattr(self.cnn, method)
        pdata = method(dataArea)
        if not pdata: return None
        pdata = pickle.loads(pdata)
        if 'None' in pdata: return None
        return pdata

    def rpush(self, rname, rvalue):
        rlength = self.cnn.llen(rname)
        if rlength > 5000: return False
        self.cnn.rpush(rname, rvalue)
        return rlength

    def sadd(self, sname, svalue):
        if self.cnn.scard(sname) > 5000: return False
        return self.cnn.sadd(sname, svalue)

    def set(self, name, value, time=3600 * 24 * 7):
        self.cnn.setex(name, value, time)
        return True

    def get(self, name):
        ret = self.cnn.get(name)
        if not ret: return 0
        return ret

    def __connect(self):
        pool = redis.ConnectionPool(host=self.host, port=self.port, db=0)
        cnn = redis.Redis(connection_pool=pool, socket_timeout=10)
        return cnn


rc = Redis_Client()
