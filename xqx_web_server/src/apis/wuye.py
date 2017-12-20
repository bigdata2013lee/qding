#coding=utf-8
import logging
import random

import re

from apis.aptm import AptmQueryApi
from apis.base import BaseApi
from models.account import QdUser
from models.account import WuyeUser
from models.aptm import Room, Project
from utils.tools import get_default_result
from utils import tools
from utils.permission import app_user_login_required, wuey_user_login_required

log = logging.getLogger('django')


class CommonApi(BaseApi):
    pass

class WuyeUserApi(BaseApi):
    """
    千丁Wuye User 相关操作API
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

        user = WuyeUser.objects(user_name=user_name, password=password, is_valid=True).first()
        if not user:
            result.setmsg('帐号或密码有误，请重新检查', 3)
            return result

        self._set_logined("wuye_user", user.id)

        result.setmsg('登录成功')
        return result

    def logout(self):
        """
        App User 注销
        :return:
        """
        result = get_default_result()
        self.request.session['wuye_user_id'] = ""
        self.request.session.flush()
        return result

    def create_user(self, project_id, user_name,  password=""):
        """
        创建一个物业帐号,并绑定社区项目
        :param project_id: T-string, 项目ID
        :param user_name: T-string, 用户名
        :param password: T-string, 密码(默认123456)
        :return:
        """
        default_password = "123456"
        result = get_default_result()
        project = Project.objects(id=project_id).first()
        if not project:
            return result.setmsg("无找到相应的社区项目", 3)

        if WuyeUser.is_exist_obj(user_name=user_name):
            return result.setmsg("无法创建新帐号，用户名%s已经存在" % user_name, 3)

        if not password: password = default_password
        password = tools.md5_str(password)
        user = WuyeUser(user_name=user_name, password=password, project=project)
        user.saveEx()

        return result

    @wuey_user_login_required
    def wy_change_pwd(self, old_password, new_password):
        """
        物业用户修改登陆密码
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

        if user.password != tools.md5_str(old_password):
            return result.setmsg("输入的旧密码错误", 3)

        user.password = tools.md5_str(new_password)
        user.saveEx()
        result.setmsg("修改密码完成")
        return result



