# -*- coding: utf-8 -*-

import functools
import logging
log = logging.getLogger("django")

# 管理员登录权限-装饰器
def mgr_login_required(func):
    user_type = "mgr_user"

    @login_required(user_type=user_type)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# 普通app 用户登录权限-装饰器
def app_user_login_required(func):
    user_type = "app_user"

    @login_required(user_type=user_type)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# 物业帐号登录权限-装饰器
def wuey_user_login_required(func):
    user_type = "wuye_user"

    @login_required(user_type=user_type)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# 通用登录权限-装饰器
def common_login_required(func):
    user_type = "common"

    @login_required(user_type=user_type)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# aio, gate 登录权限-装饰器
def public_dev_login_required(func):
    user_type = "public_device"

    @login_required(user_type=user_type)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# wuey_user, aio, gate 登录权限-装饰器
def community_login_required(func):
    user_type = "community"

    @login_required(user_type=user_type)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper



# 权限登录装饰器
def login_required(user_type):
    """
    登录权限验证
    :param user_type: mgr_user, wuye_user, app_user, gate, common, public_device
    :notice:common指允许所有类型的客户端
    """

    def out_wrapper(func):
        @functools.wraps(func)
        def in_wrapper(self, *args, **kwargs):
            _map = {
                'common': ['mgr_user', 'wuye_user', 'app_user', 'gate', 'aio'],
                'community': ['aio', 'gate', 'wuye_user'],
                'public_device': ['aio', 'gate'],
            }

            result = {'err': 0, 'msg': '', 'data': {}}

            if not self.request:
                result['err'] = 1
                result['msg'] = '未设置Request对象'
                return result

            elif not self.request.session.get("is_logined", False):
                result['err'] = 2
                result['msg'] = '用户/设备未登录'
                return result

            log.debug("input_user_type:%s, user_type:%s", user_type, self.request.session.get("user_type", ""))

            if user_type in ['common', 'public_device', 'community'] and (self.request.session.get("user_type", "") not in _map[user_type]):
                result['err'] = 4
                result['msg'] = '操作未授权'

            elif user_type in ['mgr_user', 'wuye_user', 'app_user', 'gate', 'aio'] and user_type != self.request.session.get("user_type", ""):
                result['err'] = 4
                result['msg'] = '操作未授权'

            else:
                result = func(self,  *args, **kwargs)
                
            return result
        return in_wrapper
    return out_wrapper
