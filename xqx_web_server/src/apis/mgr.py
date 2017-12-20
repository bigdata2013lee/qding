#coding=utf-8
import logging

import re

from apis.base import BaseApi
from models.account import MgrUser
from utils.tools import get_default_result
from utils import tools
from utils.permission import mgr_login_required

log = logging.getLogger('django')


class CommonApi(BaseApi):
    pass

class MgrUserApi(BaseApi):
    """
    千丁管理 User 相关操作API
    """

    def login(self, user_name, password):
        """
        Wuye User 登陆
        :param user_name: T-string, 用户名
        :param password: T-string, 密码
        :return: data -> {}
        """
        result = get_default_result()

        if not user_name or not password:
            return result.setmsg('登陆失败，请输帐号及密码！', 3)

        password = tools.md5_str(password)

        user = MgrUser.objects(user_name=user_name, password=password, is_valid=True).first()
        if not user:
            result.setmsg('帐号或密码有误，请重新检查', 3)
            return result

        self._set_logined("mgr_user", user.id)

        result.setmsg('登录成功')
        return result

    def logout(self):
        """
        App User 注销
        :return:
        """
        result = get_default_result()
        self.request.session['mgr_user_id'] = ""
        self.request.session.flush()
        return result

    @mgr_login_required
    def mgr_change_pwd(self, old_password, new_password):
        """
        管理员用户修改登陆密码
        :param old_password: T-string, 旧密码
        :param new_password: T-string, 新密码
        :return: data->{}

        :notice: 新密码要求满足格式 "^[#@_\-A-Za-z0-9]{4,30}$"
        """

        result = get_default_result()
        user = self._get_login_user()
        
        if not new_password or not re.findall("^[#@_\-A-Za-z0-9]{4,30}$", new_password):
            return result.setmsg("新密码格式错误", 3)

        if old_password == new_password:
            return result.setmsg("新密码不能与旧密码相同", 3)

        if not tools.md5_str(user.password) == tools.md5_str(old_password):
            return result.setmsg("输入的旧密码错误", 3)

        user.password = tools.md5_str(new_password)
        user.saveEx()

        return result


