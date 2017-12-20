# -*- coding:utf-8 -*-
import datetime, ctypes
from collections import defaultdict
from django.db import models


def encode(data):
    def _any(data):
        if isinstance(data, (type(None), int, float, str)):
            ret = data
        elif isinstance(data, bytes):
            ret = data.decode('utf8')
        elif isinstance(data, (dict, defaultdict)):
            ret = _dict(data)
        elif isinstance(data, (list, tuple)):
            ret = _list(data)
        elif isinstance(data, models.query.QuerySet):
            # Actually its the same as a list ...
            ret = _list(data)
        elif isinstance(data, models.Model):
            ret = _model(data)
        elif isinstance(data, ctypes.Structure):
            ret = _struct(data)
        elif isinstance(data, datetime.datetime):
            ret = data.strftime('%Y-%m-%d %H:%M:%S')
        else:
            ret = str(data)
        return ret

    def _model(data):
        ret = {}
        for f in data._meta.fields:
            ret[f.attname] = _any(getattr(data, f.attname))
        return ret

    def _struct(data):
        ret = {}
        for attr in dir(data):
            if not attr.startswith('_'):
                ret[attr] = _any(getattr(data, attr))
        return ret

    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret

    def _dict(data):
        ret = {}
        for k, v in data.items():
            ret[k] = _any(v)
        return ret

    ret = _any(data)
    return ret
