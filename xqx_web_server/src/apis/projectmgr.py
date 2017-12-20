# coding=utf8
import re
import logging
from apis.base import BaseApi
from apis.wuye import WuyeUserApi
from models.account import WuyeUser
from utils import tools
from utils.permission import mgr_login_required
from utils.tools import get_default_result
from models.aptm import Project, Room, PCity
from apis.pcity import PCityApi

log = logging.getLogger('django')


class ProjectMgrApi(BaseApi):
    """
    管理员对社区项目管理
    """
    @classmethod
    def _get_project_code(cls, ccity_id):
        """
        通过城市ID，自动生成一个可用的项目编号(8位)
        :param ccity_id: T-str, 城市ID
        :return: #str
        """
        ccity = PCity.get_ccity(ccity_id, {"area_code": "$childs.area_code", "_id": 0}) or {}
        area_code = ccity.get("area_code", "0000") or "0000"
        pre_code = area_code
        code = ""

        exist_codes = []
        for project in Project.objects(__raw__={"code": {"$regex": "^%s\d+" % pre_code}}):
            exist_codes.append(project.code)

        for x in range(1, 10000):
            _code = pre_code + "{:0>4}".format(x)
            if _code not in exist_codes:
                code = _code
                break

        return code

    def list_projects(self, pcity_id="", ccity_id="", name_like="", pager={}):
        """
        根据省/市，查询楼盘项目
        :param pcity_id: T-string, 省ID
        :param ccity_id: T-string, 市ID
        :param name_like: T-string, 项目名称模糊搜索
        :param pager: T-obj, 分页信息
        :return: data ->  {collection:[...]}
        """

        result = get_default_result()
        ccity_ids = []

        projects = Project.objects().order_by("-code")

        if ccity_id: ccity_ids = [ccity_id]
        elif pcity_id: ccity_ids = PCityApi()._get_ccity_ids(pcity_id)

        if pcity_id or ccity_id:
            projects = projects.filter(ccity_id__in=ccity_ids)

        if name_like:
            projects = projects.filter(name__contains=name_like)

        def __ex_fun(p, o):
            ccity = PCity.get_ccity(p.ccity_id)
            o['ccity_name'] = "%s %s" % (ccity.get("pname", ""), ccity.get("cname", "")) if ccity else ""

        result.data = tools.paginate_query_set(projects, pager=pager, ex_fun=__ex_fun)

        return result

    @mgr_login_required
    def add_project(self, ccity_id, project_name="", label="", street=""):
        """
        创建社区项目
        :param ccity_id: T-str, 城市ID
        :param project_name: T-str, 项目名称
        :param label: T-str, 标签
        :param street: T-str, 街道
        :return: data->{project_code:#str, project_name:#str, init_pwd:str}
        """
        result = get_default_result()

        ccity = PCity.get_ccity(ccity_id)
        if not ccity:
            return result.setmsg("选择的城市不存在", 3)
        
        project_code = self._get_project_code(ccity_id)
        wy_username, wy_password = project_code, tools.random_str()

        if Project.is_exist_obj(code=project_code):
            return result.setmsg("相同的项目编号已经存在", 3)

        if not re.findall("^[#@_\-A-Za-z0-9]{4,30}$", wy_username):
            return result.setmsg("无法创物业管理帐号，用户名%s格式错误" % wy_username, 3)

        if WuyeUser.is_exist_obj(user_name=wy_username):
            return result.setmsg("无法创物业管理帐号，用户名%s已经存在" % wy_username, 3)

        PCityApi().set_ccity_valid(ccity_id, is_valid=True)
        project = Project(ccity_id=ccity_id, code=project_code, name=project_name)
        project.label = label
        project.street = street
        project.saveEx()
        WuyeUserApi()._set_request(self.request).create_user(project.id, wy_username, password=wy_password)

        result.setdata("project_name", project_name)
        result.setdata("project_code", project_code)
        result.setdata("init_pwd", wy_password)

        result.setmsg("创建项目完成")

        return result

    @mgr_login_required
    def remove_project(self, project_id):
        """
        删除不存在房间的社区，同时删除相关的物业帐号
        :param project_id: T-str, 社区项目ID
        :return:
        """
        result = get_default_result()

        project = Project.objects(id=project_id).first()
        if not project:
            return result.setmsg("社区不存在", 3)

        if Room.is_exist_obj(project=project):
            return result.setmsg("社区存在房间，不允许删除", 3)

        wy_users = WuyeUser.objects(project=project)
        wy_users.delete()
        project.delete()

        return result

    @mgr_login_required
    def set_project_infos(self, project_id, name="", label="", street=""):
        """
        设置社区信息
        :param name: T-str, 社区名称
        :param label: T-str, 社区标签
        :param street: T-str, 社区街道
        :return data->{}
        """
        result = get_default_result()
        project = Project.objects(id=project_id).first()
        if not project:
            return result.setmsg("社区不存在", 3)

        if name: project.name = name

        project.label = label
        project.street = street
        project.saveEx()

        return result.setmsg("保存信息完成")

    @mgr_login_required
    def reset_wy_password(self, project_id):
        """
        重置物业密码
        :param project_id:　T-str, 社区项目ID
        :return: data->{project_code:#str, project_name:#str, init_pwd:str}
        """
        result = get_default_result()
        project = Project.objects(id=project_id).first()
        if not project:
            return result.setmsg("社区不存在", 3)

        wy_username, wy_password = project.code, tools.random_str()
        wy_user = WuyeUser.objects(project=project).first()

        if not wy_user:
            return result.setmsg("未找到物业帐号", 3)

        wy_user.password = tools.md5_str(wy_password)
        wy_user.saveEx()

        result.setdata("project_name", project.name)
        result.setdata("project_code", project.code)
        result.setdata("init_pwd", wy_password)

        return result.setmsg("重置物业密码完成")

