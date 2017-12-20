# -*- coding: utf-8 -*-
import time

from utils.qd import QdRds, QDEvent

__doc__ = """
间隔定时器事件
按间隔分钟或小时，产生一个相应的事件，
其它进程捕获事件后，执行相应的任务，以实现间隔定时任务
分钟事件名: interval_evt_trigger_$count_minute
小时事件名: interval_evt_trigger_$count_hour
"""
_MINUTES = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 90, 120]
_HOURS = [1, 2, 3, 4, 5, 6, 8, 12, 24, 36, 48, 60, 72, 84, 96]


def count_timer():
    if not QdRds.nx("interval_evt_trigger_count_timer", ex=60):
        return None

    rds = QdRds.get_redis()
    minutes = rds.incrby("interval_evt_trigger_minutes", amount=1)
    return minutes


def start():
    def _p():

        minutes = count_timer()
        if minutes is None: return

        for _M in _MINUTES:
            if minutes % _M != 0: continue
            QDEvent("interval_evt_trigger_%d_minute" % _M, data={"minutes": minutes}).broadcast()

        for _H in _HOURS:
            if minutes % (_H * 60) != 0: continue
            QDEvent("interval_evt_trigger_%d_hour" % _H, data={"minutes": minutes}).broadcast()

    while True:
        time.sleep(1)
        try:
            _p()

        except Exception as e:
            pass


def run():
    start()
