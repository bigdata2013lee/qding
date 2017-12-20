#coding=utf-8
import base64
import logging
import random
import re
import datetime


from conf.qd_conf import CONF
from models.common import ImageAppAvatar
from utils import misc
from apis.base import BaseApi
from utils import qd
from models.account import QdUser, AppDevice
from models.aptm import Room
from utils.qd import QdRds
from utils.tools import get_default_result, rds_api_cache
from utils import tools
from utils.permission import app_user_login_required, common_login_required, wuey_user_login_required

log = logging.getLogger('django')

class QdUserApi(BaseApi):
    """
    千丁App User 相关操作API
    """

    def _check_mobile_and_verfi_code(self, mobile, verfi_code):
        pass

    def _get_mobile_verfi_code(self, mobile):
        """
        获取手机验证码
        :param mobile: T-string, 手机号码
        :return: T-string
        """
        if not mobile or not re.findall('^1\d{10}$', mobile): return ""
        rds = QdRds.get_redis()
        verfi_code = (rds.get("mobile_verfi_code_%s" % mobile) or b'').decode("utf-8")
        return verfi_code

    def _bind_aptm(self, user, aptm, op_user=None, reason=""):
        """
        绑定房间
        :param user:
        :param aptm:
        :return:
        """

        user.related_aptms = [_.id for _ in Room.objects(id__in=[_aptm.id for _aptm in user.related_aptms])]
        if aptm not in user.related_aptms: user.related_aptms.append(aptm)
        if user not in aptm.residents: aptm.residents.append(user)

        old_master = aptm.master
        if not aptm.master: aptm.master = user

        user.update(related_aptms=user.related_aptms, updated_at=datetime.datetime.now())
        aptm.saveEx()

        QdUserNotifyApi._notify_user_aptm_change(aptm, [str(user.id)], reason=reason,
                                                 op_user=op_user, op_type="bind", alias=[str(user.id)])

        if old_master != aptm.master:
            QdUserNotifyApi._notify_aptm_master_change(aptm, aptm.master, op_user=op_user)

        return True

    def _unbind_aptm(self, users, aptm, op_user=None, reason=""):
        """
        解除绑定房间
        :param users:
        :param aptm:
        :return:
        """

        if not isinstance(users, list): users = [users]
        old_master = aptm.master

        for user in users:
            if aptm in user.related_aptms: user.related_aptms.remove(aptm)
            if user in aptm.residents: aptm.residents.remove(user)
            user.update(related_aptms=user.related_aptms, updated_at=datetime.datetime.now())

        if aptm.master in users:
            aptm.master = aptm.residents[0] if aptm.residents else None

        aptm.saveEx()

        user_ids = ["%s" % user.id for user in users]
        QdUserNotifyApi._notify_user_aptm_change(aptm, user_ids, reason=reason, op_user=op_user, op_type="unbind")

        if old_master != aptm.master:
            QdUserNotifyApi._notify_aptm_master_change(aptm, aptm.master, op_user=op_user)

        return True


    def send_mobile_verfi_code(self, mobile):
        """
        发送手机验证码
        :param mobile: T-string, 手机号码
        :return: data->{}
        """

        result = get_default_result()
        if not mobile or not re.findall('^1\d{10}$', mobile):
            return result.setmsg("%s是不正确的手机号码" % mobile, 3)

        verfi_code = random.randint(100000, 999999)
        rds = QdRds.get_redis()
        rds.set("mobile_verfi_code_%s" % mobile, "%d" % verfi_code, ex=60)

        log.debug('send verfi code[%s] to mobile[%s]', verfi_code, mobile)

        # todo del next line
        result.data['verfi_code'] = verfi_code # 测试期间输出到结果中
        # todo send verfi code to mobile

        try:
            tools.send_mobile_msg(mobile, "小亲象App登陆验证码: %s,有效期一分钟。" % verfi_code)
        except Exception as e:
            log.warning("发送手机验证码失败")
            log.exception(e)
            return result.setmsg("发送手机验证码失败", 3)


        return result

    def login(self, mobile, password_token):
        """
        App User 登陆
        :param mobile: T-string, 手机号
        :param password_token: T-string, 密码(加密)
        :return: data -> {}
        """
        result = get_default_result()

        if not mobile or not password_token:
            return result.setmsg('登陆失败，请输入手机号或密码！', 3)

        dpassword = password_token

        user = QdUser.objects(domain="sz.qdingnet.com", mobile=mobile, dpassword=dpassword, is_valid=True).first()
        if not user:
            result.setmsg('您的帐号已经在别处登陆', 5)
            return result

        self._set_logined("app_user", user.id)

        evt_data = dict(app_user_id="%s" % user.id, login_token=user.dpassword)

        # todo 主题需要修改
        qd.QDEvent("login_by_mobile_verfi_code", project_id="", data=evt_data).broadcast()
        
        result.setmsg('登录成功')
        return result



    def logout(self):
        """
        App User 注销
        :return:
        """
        result = get_default_result()
        self.request.session['app_user_id'] = ""
        self.request.session.flush()
        return result


    def login_by_mobile_verfi_code(self, mobile, verfi_code):
        """
        App User 通过手机验证码登陆
        :param mobile: T-string, 手机号
        :param verfi_code: T-string, 手机验证码
        :return: data->{"login_token":#string}
        :notice: 如果用户未注册，实现用户帐号注册
        """

        result = get_default_result()

        if not mobile or not re.findall('^1\d{10}$', mobile):
            return result.setmsg("无法注册，%s是不正确的手机号码" % mobile, 3)

        if verfi_code and self._get_mobile_verfi_code(mobile) != verfi_code:
            return result.setmsg("无法注册，手机验证码错误", 3)

        user = QdUser.objects(domain="sz.qdingnet.com", mobile=mobile).first()
        if not user:
            user_name = tools.get_uuid()
            user = QdUser(domain="sz.qdingnet.com", mobile=mobile, user_name=user_name)

        dpassword = tools.md5_str(tools.get_uuid())
        user.dpassword = dpassword
        user.saveEx()

        self._set_logined("app_user", user.id)
        self.request.session['login_token'] = user.dpassword
        result.data['login_token'] = user.dpassword

        evt_data = dict(app_user_id="%s" % user.id, login_token=user.dpassword)
        qd.QDEvent("login_by_mobile_verfi_code", project_id="", data=evt_data).broadcast()

        return result

    def login_by_outer_data(self, domain, outer_user_id):
        """
        外部App登陆
        :param domain: T-str, 域
        :param outer_user_id: T-str, 外部用户ID
        :return: data->{"login_token":#string}
        :notice: 如果用户未注册，实现用户帐号注册
        """
        from apis.outer.bjqd import BjQdingApi
        result = get_default_result()

        if not outer_user_id:
            return result.setmsg("登陆参数错误", 3)

        if domain == "www.qdingnet.com":
            fg, msg, user = BjQdingApi._login_by_member_id(outer_user_id)

            if not fg:
                return result.setmsg(msg, 3)
            else:
                dpassword = tools.md5_str(tools.get_uuid())
                user.dpassword = dpassword
                user.saveEx()
                result.data['login_token'] = dpassword

                self._set_logined("app_user", user.id)
                self.request.session['login_token'] = user.dpassword
                
                return result

        return result


    @app_user_login_required
    def change_moblie(self, mobile, verfi_code):
        """
        App User 用户修改手机号

        :param mobile: T-string, 新手机号
        :return: data->{}

        :notice:  修改手机号前，先检查新的手机号是否被占用，被占用则不对更换
        """
        result = get_default_result()
        user = self._get_login_user()
        if not mobile or not re.findall('^1\d{10}$', mobile):
            return result.setmsg("无法更换,%s是不正确的手机号码" % mobile, 3)

        if verfi_code and self._get_mobile_verfi_code(mobile) != verfi_code:
            return result.setmsg("无法更换，手机验证码错误", 3)

        exist_user = QdUser.objects(mobile=mobile).first()
        if exist_user:
            return result.setmsg("无法更换，您的手机号:%s已经被使用" % mobile, 3)

        user.mobile = mobile
        user.saveEx()
        return result

    @app_user_login_required
    def bind_aptm(self, aptm_id):
        """
        App User 绑定房间
        :param aptm_id: T-string, 房间ID
        :return: data -> {}
        """

        result = get_default_result()
        user = self._get_login_user()
        aptm = Room.objects(id=aptm_id).first()

        if not aptm:
            return result.setmsg("无法匹配房间:%s" % aptm_id, 3)

        self._bind_aptm(user, aptm, op_user=user)

        return result

    @common_login_required
    def bind_aptm_by_mobile(self, mobile, aptm_id):
        """
        通过手机号绑定房间
        如果手机帐号未创建，则创建一个帐号
        :param mobile: T-string, 手机号
        :param aptm_id: T-string, 房间ID
        :return: data->{}

        :notice: 仅供 [物业 ]及 [千丁管理员] 使用的接口
        """
        result = get_default_result()

        aptm = Room.objects(id=aptm_id).first()

        if not mobile or not re.findall('^1\d{10}$', mobile):
            return result.setmsg("无法绑定，%s是不正确的手机号码" % mobile, 3)

        if not aptm:
            return result.setmsg("无法绑定，房间不存在", 3)

        user = self._get_login_user()
        qduser = QdUser.objects(mobile=mobile).first()

        if not qduser:
            # 生成用户帐号
            user_name = tools.get_uuid()
            dpassword = tools.md5_str(tools.get_uuid())
            qduser = QdUser(domain=aptm.domain, mobile=mobile, user_name=user_name, dpassword=dpassword)
            qduser.saveEx()

        self._bind_aptm(qduser, aptm, op_user=user)
        return result.setmsg("成功绑定手机用户")

    @app_user_login_required
    def bind_aptm_by_agw_mac(self, agw_mac, aptm_id=""):
        """
        通过报警网关MAC绑定房间
        :param agw_mac: T-string, 报警网关MAC
        :param aptm_id: T-string, 房间ID, 可选参数，用于加强校验
        :return: data->{aptm:#obj}
        """
        from models.device import AlarmGateway
        result = get_default_result()
        user = self._get_login_user()
        agw_mac = (agw_mac or "").upper()

        if not re.findall("^([A-F0-9]{2}:){5}[A-F0-9]{2}$", agw_mac):
            return result.setmsg("报警网关MAC地址:%s格式错误" % agw_mac, 3)

        agw = AlarmGateway.objects(mac=agw_mac).first()
        if not agw:
            return result.setmsg("报警网关MAC地址:%s未注册设备" % agw_mac, 3)

        aptm = agw.aptm
        if not aptm or (aptm_id and str(aptm.id) != aptm_id):
            return result.setmsg("报警网关MAC地址:%s未关联房间" % agw_mac, 3)

        if user in aptm.residents:
            return result.setmsg("您已经绑定此房间", 3)

        self._bind_aptm(user, aptm, op_user=user)

        result.data['aptm'] = aptm.outputEx()

        return result

    @app_user_login_required
    def unbind_aptm(self, aptm_id):
        """
        App User 解除绑定房间
        :param aptm_id: T-string, 房间ID
        :return: data -> {}
        """

        result = get_default_result()
        user = self._get_login_user()
        aptm = Room.objects(id=aptm_id).first()

        if not aptm:
            return result.setmsg("无法匹配房间:%s" % aptm_id, 3)

        self._unbind_aptm(user, aptm, op_user=user)
        return result

    @common_login_required
    def unbind_aptm_by_user_ids(self, user_ids, aptm_id):
        """
        解绑某房间下的多个用户
        :param user_ids: T-list, 用户ID列表
        :param aptm_id: T-string, 房间ID
        :return: data ->  {}
        :notice:支持物业 或 房间管理员App User 操作此接口
        """

        result = get_default_result()
        aptm = Room.objects(id=aptm_id).first()
        op_user = self._get_login_user()

        if not aptm:
            return result.setmsg("无法匹配房间:%s" % aptm_id, 3)

        if op_user.__class__.__name__ == QdUser.__name__ and op_user != aptm.master:
            return result.setmsg("您无权限解绑其它住户", 3)

        users = []
        for user_id in user_ids:
            user = QdUser.objects(id=user_id).first()
            users.append(user)

        self._unbind_aptm(users, aptm, op_user=op_user)

        return result

    @app_user_login_required
    def get_bind_aptms(self):
        """
        App User 获取绑定的房间列表
        :return: data->{collection:[...]}
        """
        result = get_default_result()
        user = self._get_login_user()
        result.data_collection = []
        for aptm in user.related_aptms:
            result.data_collection.append(aptm.outputEx())
        return result

    @app_user_login_required
    def set_agw_notice_settings(self, option_name, enable=True):
        """
        App User 设置报警网关相关的通知选项

        :param option_name: T-string, 选项名
        :param enable: T-boolean, true-启用, true-禁用
        :return: data->{}

        :notice: 选项说明

            报警通知 - alarm
            延时报警通知 - delay_alarm
            布撤防通知 - bcf
            离线通知 - offline
        """
        result = get_default_result()
        user = self._get_login_user()

        option_names = ['alarm', 'delay_alarm', 'bcf', 'offline']
        if option_name not in option_names:
            return result.setmsg("option_name:%s 参数错误" % option_name, 3)

        user.settings["agw_notice"].update({option_name: True if enable else False})
        user.saveEx()

        return result

    @app_user_login_required
    def set_cloud_talk_settings(self, settings={}):
        """
        保存/更新 对讲相关的配置选项
        :param settings: T-dict/json 所有对讲相关的配置项
        :return: data -> {}
        """
        result = get_default_result()
        user = self._get_login_user()
        user.settings["cloud_talk"] = settings or {}
        user.saveEx()
        return result

    @app_user_login_required
    def get_settings(self, section_name=""):
        """
        获取指定的配置项目（配置集）
        :param section_name: T-str, 配置项名称, 当section_name为空时，获取到所有的配置信息
        :return: data->{"settings":{...}}
        """

        result = get_default_result()
        user = self._get_login_user()
        _settings = {}

        if not section_name:
            _settings.update(user.settings)
        else:
            _settings.update({section_name:user.settings.get(section_name, {})})

        result.data['settings'] = _settings
        return result


    def _transfer_master_role(self, aptm, user1, user2):
        """
        移交管理权限 user1 的管理权限移交给user2
        :param aptm:
        :param user1:
        :param user2:
        :return:
        """

        if not aptm or not user1 or not user2:
            return False, "移交管理权限失败"

        if user1 != aptm.master:
            return False, "移交管理权限失败"

        if not (user1 in aptm.residents and user2 in aptm.residents):
            return False, "移交管理权限失败"

        aptm.master = user2
        aptm.saveEx()

        QdUserNotifyApi._notify_aptm_master_change(aptm, aptm.master, op_user=user1)

        return True, ""

    @app_user_login_required
    def transfer_master_role(self, aptm_id, to_user_id):
        """
        移交管理权限
        :param aptm_id: T-string, 房间ID
        :param to_user_id: T-string, 新管理员ID
        :return: data->{}
        """

        result = get_default_result()
        user = self._get_login_user()
        to_user = QdUser.objects(id=to_user_id).first()

        aptm = Room.objects(id=aptm_id).first()

        success, msg = self._transfer_master_role(aptm, user, to_user)

        if not success:
            return result.setmsg(msg, 3)

        return result

    @wuey_user_login_required
    def wy_set_aptm_master(self, aptm_id, user_id):
        """
        物业设置家庭管理员
        :param aptm_id: T-string, 房间ID
        :param user_id: T-string, 新管理员ID
        :return: data->{}
        """
        result = get_default_result()
        user = self._get_login_user()

        qduser = QdUser.objects(id=user_id).first()
        aptm = Room.objects(id=aptm_id).first()

        if not aptm or not qduser or qduser not in aptm.residents or aptm.master == qduser:
            return result.setmsg("设置家庭管理员失败", 3)

        aptm.master = qduser
        aptm.saveEx()

        QdUserNotifyApi._notify_aptm_master_change(aptm, qduser, op_user=user)

        return result

    @app_user_login_required
    @rds_api_cache(ex=60, think_session=True)
    def is_aptm_master(self, aptm_id):
        """
        判断当前用户是否为某个房间的Master
        :param aptm_id: T-string, 房间ID
        :return: data->{is_master:#bool}
        """
        from apis.outer.bjqd import BjQdingApi
        user = self._get_login_user()

        result = get_default_result()
        aptm = Room.objects(id=aptm_id).first()
        if not aptm:
            result.setdata("is_master", False)
            return result

        user_outer_id = user.source_data_info.get("outer_id", "")
        aptm_outer_id = aptm.source_data_info.get("outer_id", "")

        fg = BjQdingApi._is_aptm_master(user_outer_id, aptm_outer_id)

        result.setdata("is_master", fg)
        return result


    @app_user_login_required
    def me(self):
        """
        获取当前用户信息
        :return:data->{user:#obj}
        """
        result = get_default_result()
        user = self._get_login_user()
        result.data['user'] = user.outputEx()
        return result


    @app_user_login_required
    def get_family_members(self, aptm_id, include_me=False):
        """
        获取与自己绑定同一房间的家庭成员信息（同一房屋的APP User）
        :param aptm_id: T-string, 房间ID
        :param include_me: T-boolean, 是否包括自己，默认否
        :return: data->{collection:[{id:#string, mobile:#string, name:#string},...]}
        """

        result = get_default_result()
        result.data_collection = []
        me = self._get_login_user()

        aptm = Room.objects(id=aptm_id).first()
        if not aptm:
            log.warning("Not found aptm by id:%s", aptm_id)
            return result

        for user in aptm.residents:
            if not include_me and user == me: continue
            result.data_collection.append(dict(id=str(user.id), mobile=user.mobile, name=user.name, updated_at=int(user.updated_at.timestamp() * 1000)))

        return result


    def get_aptm_residents(self, aptm_id):

        """
        获取家庭下所有住户
        :param aptm_id:
        :return:
        """
        result = get_default_result()
        result.data_collection = []
        aptm = Room.objects(id=aptm_id).first()
        if not aptm:
            log.warning("Not found aptm by id:%s", aptm_id)
            return result

        for user in aptm.residents:
            result.data_collection.append(user.outputEx())

        return result

    @app_user_login_required
    def set_avatar(self, img_base64):
        """
        用户设置个人头像
        :param img_base64: T-string, 图片的base64编码
        :return: data->{}

        :notice: 下载头像文件地址 http(s)://$host/image/app/avatars/$user_id
        """
        result = get_default_result()
        user = self._get_login_user()

        if not img_base64 or not isinstance(img_base64, str):
            return result.setmsg("保存头像失败，img_base64参数错误", 3)

        fsize = 0
        try:  # 进一步检测合法性
            img = base64.standard_b64decode(img_base64)
            fsize = len(img)

        except Exception as e:
            return result.setmsg("保存头像失败", 3)

        avatar = user.avatar
        if not avatar: avatar = ImageAppAvatar()

        avatar.base64 = img_base64
        avatar.fsize = fsize
        avatar.saveEx()

        user.avatar = avatar
        user.saveEx()

        return result.setmsg("设置头像完成")

    @app_user_login_required
    def edit_profile(self, nickname="", gender="M"):
        """
        用户修改个人资料
        :param nickname: T-string, 昵称
        :param gender: T-string, 姓别 M-男, F-女
        :return: data->{}
        """

        result = get_default_result()
        user = self._get_login_user()

        if nickname:
            user.name = nickname
        if gender in ['M', 'F']:
            user.gender = gender

        user.saveEx()
        return result

    @app_user_login_required
    def validate_last_login_token(self):

        """
        验证当前的User App是否为最后一个登陆的客户端
        @notice: App收到登陆通知后，调用此接口
        :return: data->{validate:#boolean}
        """
        result = get_default_result()
        user = self._get_login_user()

        if self.request.session.get('login_token', '') != user.dpassword:
            result.setdata("validate", False)
        else:
            result.setdata("validate", True)

        return result

    @app_user_login_required
    def report_app_device_info(self, manufacturer="", model="", build_id="", sdk="", rom=""):
        """
        App 登陆后，调用此接口，上报客户端设备信息
        :param manufacturer:
        :param model:
        :param build_id:
        :param sdk:
        :param rom:
        :return: data->{}
        """
        result = get_default_result()
        user = self._get_login_user()

        app_dev = AppDevice.objects(user=user).first()
        if not app_dev: app_dev = AppDevice()
        app_dev.set_attrs(manufacturer=manufacturer, model=model, build_id=build_id, sdk=sdk, rom=rom)
        app_dev.saveEx()
        return result




class QdUserNotifyApi(BaseApi):

    @classmethod
    def _notify_user_aptm_change(cls, aptm, user_ids, op_type="bind", reason="", op_user=None, alias=[]):
        """
        房屋住户变化通知
        :param aptm: T-doc, 房间
        :param user_ids: T-list<#str>, 新增或删除的AppUser ids
        :param op_type: T-str, 操作类型 bind|unbind
        :param reason: T-str, 操作原因
        :param op_user: T-doc, 有权限操作的系统帐户或AppUser
        :param alias: T-str, 用于单独推送给某个AppUser(适用于绑定房间的情况, 因为新绑定的App,未注册房间Tag)
        """
        if not user_ids or not aptm: return
        Enum = misc.NoticeTypesEnum
        msg_type = Enum.user_aptm_bind_change if op_type == "bind" else Enum.user_aptm_unbind_change

        log.debug("tag:%s", str(aptm.id))
        user_ids = user_ids
        aptm_name = aptm.get_aptm_short_name()

        msg_data = dict(user_ids=user_ids, aptm_id="%s" % aptm.id, aptm_name=aptm_name,
                        op_user="%s:%s" % (op_user.__class__.__name__, op_user.id) if op_user else "",
                        master_id=str(aptm.master.id) if aptm.master else "", reason=reason)

        extras = {"msg_type": msg_type, "msg_data": msg_data}
        log.debug("notify_user_aptm_change extras:%s", extras)
        tools.send_push_message(content="", extras=extras, alias=alias, tags=str(aptm.id), domains=aptm.domain)

    @classmethod
    def _notify_aptm_master_change(cls, aptm, master, op_user=None):
        """
        房屋管理员变化通知
        :param aptm: T-doc, 房间
        :param master:T-doc, 被设置为管理员的AppUser
        """
        if not aptm: return
        Enum = misc.NoticeTypesEnum
        aptm_name = aptm.get_aptm_short_name()
        msg_data = dict(aptm_id="%s" % aptm.id, aptm_name=aptm_name,
                        op_user="%s:%s" % (op_user.__class__.__name__, op_user.id) if op_user else "",
                        master_id=str(master.id) if master else "")
        extras = {"msg_type": Enum.aptm_master_change, "msg_data": msg_data}
        tools.send_push_message(content="", extras=extras, tags=str(aptm.id), domains=aptm.domain)


        

class QdUserQRCodeApi(BaseApi):

    @app_user_login_required
    @rds_api_cache(300, think_session=True)
    def get_aptm_bind_qrc_url(self, aptm_id):
        """
        获取服务器生成的绑定房间的二维码URL
        :param aptm_id: T-string, 房间ID
        :return: data->{"url":"$host/qrcode/bind_aptm/$qrcode"}
        """
        result = get_default_result()
        user = self._get_login_user()
        aptm = Room.objects(id=aptm_id).first()

        if not aptm:
            return result.setmsg("房屋信息不正确", 3)

        if user and aptm.master != user:
            return result.setmsg("非Master，不能生成二维码", 3)

        rds = QdRds.get_redis()

        with qd.DistributedLock("QdUserQRCodeApi_get_aptm_bind_qrc_url"):
            qr_code_index = rds.incr("QRCodeIndex")
            if qr_code_index >= 99999999:rds.set("QRCodeIndex", 0)

            qr_code_index_str = tools.decode_int(qr_code_index)

            rds.set("qrcode_index_str:%s" % qr_code_index_str, "bind_aptm:%s" % aptm_id, ex=3600*24)
            url = "%s/qrcode/bind_aptm/%s" % (self._get_http_scheme_host(), qr_code_index_str)
            result.setdata("url", url)

        return result

    @app_user_login_required
    def app_bind_aptm_by_qrc(self, qrcode_str, user_id):
        """
        App用户通过二维码绑定房间
        :param qrcode_str: T-string, 二维码标识串
        :param user_id: T-string, 用户ID
        :return: data->{infos:{aptm_id:#str, aptm_name:#str, master_id:#str}}
        """
        result = get_default_result()
        user = self._get_login_user()
        _user = QdUser.objects(id=user_id).first()
        rds = QdRds.get_redis()
        rds_key = "qrcode_index_str:%s" % qrcode_str
        rds_val = rds.get(rds_key)

        if not user or user != _user: return result.setmsg("用户信息错误", 3)
        if not rds_val: return result.setmsg("无效或过期的二维码", 3)

        _find = re.findall("bind_aptm:(\w+)", rds_val.decode("utf-8"))

        aptm = Room.objects(id=_find[0]).first() if _find else None

        if not aptm:
            return result.setmsg("房屋信息错误", 3)

        if user not in aptm.residents:
            qduser_api = QdUserApi()._set_request(self.request)
            qduser_api.bind_aptm("%s" % aptm.id)

        else:
            return result.setmsg("房屋已经绑定", 3)

        result.setdata("infos", dict(aptm_id="%s" % aptm.id, aptm_name=aptm.get_aptm_full_name(),
                                     master_id="%s" % aptm.master.id if aptm.master else ""))
        return result


