# coding=utf-8

import json
import logging
import time
import threading

import requests

from conf.qd_conf import CONF
from models.account import QdUser
from models.aptm import Room
from utils.qd import QdRds

__doc__ = """

"""
log = logging.getLogger('bjqdpush')

rds = QdRds.get_redis()

test_data_records = []


def send_push_message(**kwargs):

    try:
        _send_bjpush(**kwargs)

    except Exception as e:
        log.exception(e)


def _request(params):

    headers = {}
    headers['user-agent'] = 'xqx-python-client'
    headers['content-type'] = 'application/json;charset:utf-8'
    session = requests.Session()

    url = CONF.get("domain").get("www.qdingnet.com").get("apis").get("push_api")

    _body_params = {"body": json.dumps(params, ensure_ascii=False)}
    log.debug("Request qdjd_push url: %s", url)
    log.debug("Request qdjd_push _body_params: %s", _body_params)
    try:
        response = session.request('POST', url, params=_body_params, headers=headers, timeout=10)
        res_data = response.content.decode("utf-8")
        log.debug(res_data)

    except Exception as e:
        log.error("请求北京推送接口异常")
        log.exception(e)


def _send_bjpush(content="", extras={}, alias=[], tags=[]):
    """
    发送北京消息推送
    :param content: T-string, 消息内容
    :param alias: T-list, 用户/设备ID 列表
    :param tags: T-list, 组 列表

    :notice: etc -> {"mids":[],"roomIds":[],"params":{"alerttitle":"","isShowNotify":0,"action":{"msg_title":"msg title ","msg_type":12,"msg_data":{}}},"curTime":1489391079,"tid":"roomPushNotify"}
    """

    _extras = {"msg_title": content, "msg_type": "", "msg_data": {}}
    if extras: _extras.update(extras)

    log.debug("original alias:%s", alias)
    log.debug("original tags:%s", tags)

    domain = "www.qdingnet.com"
    if alias: alias = ["%s" % u.source_data_info.get("outer_id", "") for u in QdUser.objects(domain=domain, id__in=alias)]
    if tags: tags = ["%s" % r.source_data_info.get("outer_id", "") for r in Room.objects(domain=domain, id__in=tags)]

    message = {
        "alerttitle": _extras.get("msg_title", ""),
        "isShowNotify": 0,
        "action": _extras,
    }
    req_params = {
        "curTime": "%d" % time.time(),
        "tid": "SzXqxPushNotify",
        # "contentAvailable": 1,
        "mids": alias,
        "roomIds": tags,
        "params": message
    }

    try:
        _request(req_params)
    except Exception as e:
        log.exception(e)


def _get_message():

    try:
        _params_data = rds.rpop("bj_push") or b'{}'
        _params = json.loads(_params_data.decode("utf-8"))
        return _params

    except Exception as e:
        log.exception(e)
        return None


def run_task1(thead_count=2):

    def _do_task():
        while True:
            params = _get_message()

            if not params:
                time.sleep(2)
                continue

            send_push_message(**params)

    threads = []

    for num in range(0, thead_count):
        t = threading.Thread(target=_do_task)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


def run():
    run_task1(thead_count=10)

