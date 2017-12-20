# coding=utf-8

import logging
from utils.qdevt import QdEventExecutor

log = logging.getLogger("qdcommevts")
evt_executor = QdEventExecutor()


@evt_executor.bind_handler
class EvtHandler(object):
    handler_name = "qdcommevts"
    etype_patterns = [
        "missed_call", "login_by_mobile_verfi_code",
        #...
        'agw_alarm_area_change', 'agw_unbind',
    ]

    

    @classmethod
    @evt_executor.on("missed_call")
    def do_missed_call(cls, qdevt):
        from models.aptm import Room
        aptm_id = qdevt.data.get("aptm", "")
        # todo somethings
        



def run():

    evt_executor.run_threads(thead_count=12)
