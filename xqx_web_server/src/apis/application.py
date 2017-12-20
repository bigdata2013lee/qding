# coding=utf-8

import logging
from apis.qduser import QdUserApi, QdUserNotifyApi
from utils import qd
from apis.base import BaseApi
from models.common import AptmApplication
from utils import tools
from utils.qd import QdRds
from utils.tools import get_default_result
from models.aptm import Room
from utils import misc
from utils.permission import app_user_login_required, wuey_user_login_required

log = logging.getLogger('django')

__doc__ = """
App user 向物业申请绑定审核 相关功能API
"""


class ApplicationApi(BaseApi):
    """
    App user 向物业申请绑定审核 相关功能API
    """

    @app_user_login_required
    def report_atpm_application(self, aptm_id, user_realname="", user_type="", user_notice=""):
        """
        App用户申请房间绑定
        :param aptm_id: T-string, 绑定房间的ID
        :param user_realname: T-string, 住户的真实姓名
        :param user_type: T-string, 住户身份
        :param user_notice: T-string, 用户填写的申请备注
        :return: data->{}
        """

        result = get_default_result()
        user = self._get_login_user()
        aptm = Room.objects(id=aptm_id).first()

        if not aptm:
            return result.setmsg("需要绑定的房间不存在", 3)

        if user in aptm.residents:
            return result.setmsg("你已经绑定了此房间", 3)

        if not QdRds.nx("nx_report_atpm_application_aptm_%s_user_%s" % (aptm_id, user.id), ex=3600):
            return result.setmsg("你最近已经提交了申请，请耐心等待审核", 3)

        target_aptm_name = aptm.get_aptm_short_name()
        application = AptmApplication(project=aptm.project, user=user, target_aptm=aptm, status="new",
                                      user_mobile=user.mobile, user_realname=user_realname,
                                      target_aptm_name=target_aptm_name,
                                      user_type=user_type or "住户", user_notice=user_notice)

        application.saveEx()

        qd.QDEvent("user_application_aptm_bind", project_id=aptm.project.id, data=application.outputEx()).broadcast()

        return result

    @wuey_user_login_required
    def wy_check_atpm_application(self, application_id, status="pass", wy_notice=""):
        """
        物业审核 App用户 房间绑定申请
        :param application_id: T-string, 申请记录ID
        :param status: T-string, 申请状态  reject|pass
        :param wy_notice: T-string, 物业填写的审核备注信息
        :return:
        """
        result = get_default_result()
        user = self._get_login_user()

        project = user.project
        application = AptmApplication.objects(project=project, domain=project.domain, id=application_id).first()

        if not application:
            return result.setmsg("申请ID不正确", 3)

        if status not in ['pass', 'reject']:
            return result.setmsg("状态参数不正确", 3)

        application.set_attrs(status=status, wy_notice=wy_notice)
        application.saveEx()

        if application.user in application.target_aptm.residents:
            return result

        # 通过，绑定用户到房间
        if status == 'pass':
            qduser_api = QdUserApi()
            qduser_api._bind_aptm(application.user, application.target_aptm, op_user=user, reason="application_pass")

        # 拒绝，发送拒绝通知到个人
        elif status == 'reject':
            extras = {"msg_type": misc.NoticeTypesEnum.reject_aptm_application, "msg_data": application.outputEx()}
            tools.send_push_message(content="绑定房间(%s)申请被拒绝" % application.target_aptm_name, extras=extras,
                                    alias=["%s" % application.user.id], domains=project.domain)

        return result

    @wuey_user_login_required
    def wy_query_aptm_applications(self, status="new", pager={}):
        """
        物业查询 App用户 房间绑定申请列表
        :param status: T-string, 申请记录状态 new|pass|reject
        :param pager: T-dict, 分页信息
        :return: data->{collection:#list}
        """
        result = get_default_result()
        user = self._get_login_user()

        applications = AptmApplication.objects(project=user.project).order_by("-updated_at")
        if status:
            applications = applications.filter(status=status)

        result.data = tools.paginate_query_set(applications, pager=pager)

        return result




