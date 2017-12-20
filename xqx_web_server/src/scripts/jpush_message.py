#coding=utf-8

import json
import logging
import time
import threading

from conf.qd_conf import CONF
from utils.qd import QdRds

__doc__ = """

"""
jpush_log = logging.getLogger('jpush')

rds = QdRds.get_redis()

test_data_records = []


def send_push_message(**kwargs):

    try:
        _send_jpush(**kwargs)
    except Exception as e:
        # TODO 解决连接失败，重发消息
        jpush_log.exception(e)


def _send_jpush(content="", extras={}, alias=[], tags=[]):
    """
    发送极光消息推送
    :param content: T-string, 消息内容
    :param alias: T-list, 用户/设备ID 列表
    :param tags: T-list, 组 列表
    :notice: alias 与 tags 不能同时存在
    """
    jpush_log = logging.getLogger('jpush')
    app_key = CONF.get("jpush").get("app_key")
    master_secret = CONF.get("jpush").get("master_secret")

    import jpush
    from jpush import common
    from jpush import alias as jpush_alias
    from jpush import tag as jpush_tag

    _jpush = jpush.JPush(app_key, master_secret)
    push = _jpush.create_push()

    # 目标
    if alias:
        push.audience = jpush.audience(jpush_alias(*alias))

    elif tags:
        push.audience = jpush.audience(jpush_tag(*tags))

    else:
        push.audience = jpush.all_

    _extras = {"msg_title": content, "msg_type": "", "msg_data": {}}
    if extras: _extras.update(extras)

    android_msg = jpush.android(alert="", extras=_extras)
    ios_msg = jpush.ios(extras=_extras, content_available=True, sound="")
    push.notification = jpush.notification(alert="", ios=ios_msg, android=android_msg)

    push.options = {"apns_production": False}
    push.platform = jpush.all_

    try:
        response = push.send()
        jpush_log.debug(response)
    except common.Unauthorized as e:
        jpush_log.exception(e)
    except common.APIConnectionException as e:
        jpush_log.exception(e)
    except common.JPushFailure as e:
        jpush_log.exception(e)
    except Exception as e:
        jpush_log.exception(e)


def _get_message():

    try:
        _params_data = rds.rpop("jpush") or b'{}'
        _params = json.loads(_params_data.decode("utf-8"))
        return _params

    except Exception as e:
        jpush_log.exception(e)
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
    run_task1(thead_count=20)

