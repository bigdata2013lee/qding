# coding=utf8
from apis.bell import DeviceApi

api_map = {}


def _add(m, *cls):
    for api_cls in cls:
        api_map["%s.%s" % (m, api_cls.__name__)] = api_cls()


_add("device", DeviceApi)
