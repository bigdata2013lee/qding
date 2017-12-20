# coding=utf-8
import logging

from utils.qdevt import QdEventExecutor

log = logging.getLogger("qdcommevts")

evt_executor = QdEventExecutor()


@evt_executor.bind_handler
class EvtHandler(object):
    handler_name = "qdcommevts"


    @classmethod
    @evt_executor.on("interval_evt_trigger_1_minute")
    def trigger_1_minute_a(cls, qdevt):
        log.debug('interval_evt_trigger_5_minute')


    @classmethod
    @evt_executor.on("trigger_break_alarm")
    def clear_api_cache_for_alarm(cls, qdevt):
        log.debug('start')
        log.debug(qdevt.data)

    @classmethod
    @evt_executor.on("trigger_agw_alarm")
    def send_alarm_to_app(cls, qdevt):
        """触发报警时，发送通知到app"""
        log.debug("触发报警时，发送通知到app")


def run():
    log.debug("run")
    evt_executor.run_threads(thead_count=12)
