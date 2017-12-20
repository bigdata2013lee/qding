# coding=utf-8

from collections import namedtuple

__doc__ = """
一些映射关系及常量定义
"""

gate_open_ways = ["card", "gate_pwd", "resident_pwd", "aptm_call", "aio_call"]

Alarm_Types_ZH = {1: "紧急", 2: "红外", 3: "燃气", 4: "门磁", 5: "窗磁", 6: "烟感", 7: "破坏"}
Alarm_Locations_ZH = {1: "客厅", 2: "卧室", 3: "厨房", 4: "阳台"}

class AlarmTypesEnum(object):
    sos = 1
    ir = 2
    gas = 3
    door = 4
    window = 5
    smoke = 6
    broken = 7


class NoticeTypesEnum(object):
    # 网关 1-9
    alarm = 1
    bcf = 2
    delay_alarm = 3
    agw_offline = 4

    # app comm 11-20
    reject_aptm_application = 11
    user_aptm_bind_change = 12
    user_aptm_unbind_change = 13
    aptm_master_change = 14
    app_user_logined = 15

    # 对讲通话 31-40
    missed_call = 31



class GateOpenWaysEnum(object):
    card = "card"
    gate_pwd = "gate_pwd"
    resident_pwd = "resident_pwd"
    aptm_call = "aptm_call"
    call_phone = "call_phone"
    app_remote = "app_remote"
    aio_call = "aio_call"

    @classmethod
    def get_vals(cls):
        return [cls.card, cls.gate_pwd, cls.resident_pwd, cls.aptm_call, cls.app_remote, cls.aio_call]



