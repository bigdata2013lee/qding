# --*-- coding:utf8 --*--
import pickle, json, re, datetime, hashlib

from mongoengine.document import Document

from apps.common.utils.redis_client import rc


def json_default(obj):
    if isinstance(obj, Document):
        return str(obj.id)
    if isinstance(obj, datetime.datetime):
        return obj.timestamp()
    else:
        raise Exception("json serialize fail")


def method_set_rds(time=3600):
    def _decorator(func):

        def __make_key(args, kargs):
            func_find = re.findall("function\s(\w+\.\w+)", str(func))
            if len(func_find) != 1: raise Exception("find function name exception")
            if len(args) > 1: raise Exception("pass parameter way exception")
            func_name = func_find[0]
            s = json.dumps(kargs, sort_keys=True, default=json_default)
            k = hashlib.md5(s.encode("utf8")).hexdigest()
            return "api_cache:%s:%s" % (func_name, k)

        def __wrapper(*args, **kargs):  #args和kargs仅为字符串和数字
            key = __make_key(args, kargs)
            result = rc.get(key)
            if not result:
                result = func(*args, **kargs)
                if result: rc.set(key, pickle.dumps(result), time)
            else:
                result = pickle.loads(result)
            return result

        return __wrapper

    return _decorator


def method_clear_rds(func_name, func_kwargs):
    """清除缓存"""
    s = json.dumps(func_kwargs, sort_keys=True, default=json_default)
    k = hashlib.md5(s.encode("utf8")).hexdigest()
    rc.cnn.delete("api_cache:%s:%s" % (func_name, k))