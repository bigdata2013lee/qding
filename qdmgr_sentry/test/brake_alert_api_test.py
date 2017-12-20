# --*-- coding:utf8 --*--

from apps.common.api.brake_api import Brake_Alert_Api
from test.test_data import web_user
alert_id = None


def test_brake_alert_api():
    test_add_alerter()
    test_set_alerter()
    test_get_alerter()
    test_delete_alerter()


def test_add_alerter():
    params = {
        "web_user_id": web_user['id'],
        "alert_email": "bigdata2013lee@163.com",
    }
    result = Brake_Alert_Api().add_alerter(**params)
    global alert_id
    alert_id = result['data'].get("alert_id")


def test_set_alerter():
    params = {
        "alert_id": alert_id,
        "alert_email": "bigdata2013lee@163.com",
    }
    Brake_Alert_Api().set_alerter(**params)


def test_get_alerter():
    params = {
        "web_user_id": web_user['id'],
    }
    Brake_Alert_Api().get_alerter(**params)


def test_delete_alerter():
    params = {
        "alert_id": alert_id,
    }
    Brake_Alert_Api().delete_alerter(**params)
