# coding=utf-8

import datetime
from json.encoder import JSONEncoder
from django.core import serializers
import time


class DateTimeJsonEncoder(JSONEncoder):
    def default(self, obj):

        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')

        elif isinstance(obj, datetime.date):

            return obj.strftime('%Y-%m-%d')

        else:
            return JSONEncoder.default(self, obj)


def jsonModel(model, fields=None, datetime2int=True, dealFun=None):
    objlist = serializers.serialize("python", [model], fields=fields)
    obj = objlist[0]
    obj.get("fields")['id'] = obj.get("pk", "")
    _jsonObj = obj.get("fields")

    for key, val in _jsonObj.items():
        if isinstance(val, datetime.datetime) and datetime2int:
            _val = int(time.mktime(val.timetuple()) * 1000 + val.microsecond / 1000)
            _jsonObj[key] = _val

        elif isinstance(val, datetime.datetime) and not datetime2int:
            _jsonObj[key] = val.strftime('%Y-%m-%d %H:%M:%S')

        elif isinstance(val, datetime.date):
            _jsonObj[key] = val.strftime('%Y-%m-%d')

        elif isinstance(val, datetime.time):
            _jsonObj[key] = val.strftime('%H:%M')

    if dealFun: dealFun(_jsonObj)
    return _jsonObj


def jsonModelList(mList, fields=None):
    return [mo.json(fields=fields) for mo in mList]
