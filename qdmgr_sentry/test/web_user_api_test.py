# --*-- coding:utf8 --*--

from apps.common.api.user_api import Web_User_Api
from test.test_data import apartment, web_user, config_user
user_id = None


def test_web_user_api():
    test_add_web_user()
    test_web_login()
    test_brake_config_login()
    test_get_user_info()
    test_bind_user_project()
    test_modify_user()
    test_forget_password()
    test_remove_web_user()


def test_add_web_user():
    params = {
        "user_type": web_user['user_type'],
        "username": web_user['username'],
        "config_password": web_user['brake_config_password'],
        "project_list": []
    }
    global user_id
    result = Web_User_Api().add_web_user(**params)
    if result['data']['flag'] == 'Y':
        user_id = result['data']['web_user'].id


def test_web_login():
    params = {
        "username": web_user['username'],
        "password": web_user['brake_config_password'],
    }
    Web_User_Api().web_login(**params)


def test_brake_config_login():
    params = {
        "province": apartment['province'],
        "city": apartment['city'],
        "community": apartment['project'],
        "phone": config_user['phone'],
        "brake_config_password": config_user['brake_config_password'],
    }
    Web_User_Api().brake_config_login(**params)


def test_get_user_info():
    params = {
        "user_id": user_id
    }
    Web_User_Api().get_user_info(**params)


def test_bind_user_project():
    params = {
        "user_id": user_id,
        "project_list": [],
    }
    Web_User_Api().bind_user_project(**params)


def test_modify_user():
    params = {
        "user_id": user_id,
        "username": web_user['username'],
        "password": web_user['password'],
        "status": "2",
        "phone": "",
        "user_type": web_user['user_type'],
    }
    Web_User_Api().modify_user(**params)


def test_forget_password():
    params = {
        "phone": config_user['phone'],
        "verify_code": "123456",
    }
    Web_User_Api().forget_password(**params)


def test_remove_web_user():
    params = {
        "user_id": user_id
    }
    Web_User_Api().remove_web_user(**params)
