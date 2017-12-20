# -*- coding: utf-8 -*-

import functools
import logging
log = logging.getLogger("django")

# 管理员登录权限-装饰器
def mgr_login_required(func):
    user_type = "mgr_user"

    @login_required(user_type=user_type)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# 普通app 用户登录权限-装饰器
def app_user_login_required(func):
    user_type = "app_user"

    @login_required(user_type=user_type)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# 物业帐号登录权限-装饰器
def wuey_user_login_required(func):
    user_type = "wuye_user"

    @login_required(user_type=user_type)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# 通用登录权限-装饰器
def common_login_required(func):
    user_type = "common"

    @login_required(user_type=user_type)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# aio, gate 登录权限-装饰器
def public_dev_login_required(func):
    user_type = "public_device"

    @login_required(user_type=user_type)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# wuey_user, aio, gate 登录权限-装饰器
def community_login_required(func):
    user_type = "community"

    @login_required(user_type=user_type)
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
            result = {'err': 0, 'msg': '', 'data': {}}

            if not self.request:
                result['err'] = 1
                result['msg'] = '未设置Request对象'
                return result

            elif not self.request.session.get("is_logined", False):
                result['err'] = 2
                result['msg'] = '用户/设备未登录'
                return result

            log.debug("user_type:%s", self.request.session.get("user_type", ""))
            if user_type == 'public_device' and self.request.session.get("user_type", "") not in ['aio', 'gate']:
                result['err'] = 4
                result['msg'] = '操作未授权'

            elif user_type == 'community' and self.request.session.get("user_type", "") not in ['aio', 'gate', 'wuye_user']:
                result['err'] = 4
                result['msg'] = '操作未授权'

            else:
                result = func(self,  *args, **kwargs)
            return result
        return in_wrapper
    return out_wrapper


















