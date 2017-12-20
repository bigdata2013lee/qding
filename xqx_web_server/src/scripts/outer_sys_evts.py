# coding=utf-8

import logging
import threading


from utils import qdevent_tools


log = logging.getLogger("outersysevts")

task_queue_name = 'outersysevts_task_queue'

subscribes = ["bjqd/*"]
set_evt_handler_cls, care_etype, listen_qdevents, run_threads, \
reg_signal_term, process_exit_status = qdevent_tools.mks(task_queue_name, subscribes, log)


class EvtHandler(object):

    @classmethod
    @care_etype("bjqd/notify_bj_room_data_change")
    def sync_bj_room_data(cls, qdevt):
        from apis.outer.bjqd import BjQdingApi
        outer_project_id = qdevt.data.get("project_id")
        BjQdingApi._sync_bj_room_data(outer_project_id)


set_evt_handler_cls(EvtHandler)


def run():
    reg_signal_term()
    evt_listen_th = threading.Thread(target=listen_qdevents)
    run_threads(thead_count=10, depend_ths=[evt_listen_th])
    process_exit_status()
