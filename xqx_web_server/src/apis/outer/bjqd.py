# coding=utf-8
import json
import logging

import requests

from apis.base import BaseApi

from conf.qd_conf import CONF
from models.account import QdUser
from models.aptm import Room
from models.device import AlarmGateway
from utils import tools
from utils.tools import get_default_result, rds_api_cache

log = logging.getLogger('django')

domain = "www.qdingnet.com"


class BjQdingApi(BaseApi):


    @classmethod
    def _request_bj_api(cls, url, params={}, timeout=10):

        """

        """
        headers = {}
        headers['user-agent'] = 'xqx-python-client'
        headers['content-type'] = 'application/json;charset:utf-8'
        session = requests.Session()
        body_params = {"body": json.dumps(params)}

        log.debug("url:%s", url)
        log.debug("body_params:%s", body_params)
        res_obj = {}
        try:
            response = session.request('POST', url, params=body_params, headers=headers, timeout=timeout)
        except Exception as e:
            log.exception(e)
            return False, "请求北京Api接口失败，网络异常。", None

        try:
            res_data = response.content.decode("utf-8")
            res_obj = json.loads(res_data)

        except Exception as e:
            log.exception(e)
            return False, "请求北京Api接口失败，Json解析错误。", None

        if res_obj.get("code", -1) not in [200]:
            return False, "请求北京Api接口失败，内部错误[code:%s] 。" % res_obj.get("code", -1), None

        return True, "", res_obj

    @classmethod
    def _login_by_member_id(cls, member_id):
        """
        通过北京用户MemberId，获取用户信息,创建用户，绑定房间
        :param member_id: T-str, 北京用户MemberId
        :return: fg, msg, #QdUser
        """
        fg, msg, info = cls._load_user_info(member_id)

        if not fg: return False, msg, None

        user = cls._create_user(info)

        if not user: return False, "无法创建用户", None

        cls._bind_local_aptms(user, info.get("member_room_ids", []))

        return True, "", user

    @classmethod
    @rds_api_cache(ex=20, think_session=False)
    def _load_user_info(cls, member_id):
        """
        通过北京用户MemberId，获取用户信息，信息中包括用户的基本信息，房间列表
        :param member_id:
        :return: {..., member_room_ids:[...]}
        """

        url = CONF.get("domain").get("www.qdingnet.com").get("apis").get("get_user_info")
        params = dict(memberId=member_id)
        flg, msg, res_json = cls._request_bj_api(url, params)

        if not flg:
            return False, msg, None

        user_data = res_json.get("data", {}).get("userData", {})
        user_base_info = dict(mobile=user_data.get("mobile", ""), outer_id=user_data.get("memberId", ""),
                              nick_name=user_data.get("nickName", ""),
                              gender="M" if user_data.get("gender", 1) else "W",
                              head_image=user_data.get("headImage", ""))

        user_base_info['member_room_ids'] = [rd.get("roomId", "") for rd in user_data.get("memberRoomDataList", [])]

        return True, "", user_base_info

    @classmethod
    def _create_user(cls, user_base_info):
        """
        通过外部信息构建一个 xqx 用户
        :param user_base_info: T-dict
        :return: #QdUser
        """

        outer_id = user_base_info.get("outer_id", "")
        mobile = user_base_info.get("mobile", "")
        nick_name = user_base_info.get("nick_name", "")
        gender = user_base_info.get("gender", "M")

        dpassword = tools.md5_str(tools.get_uuid())

        if not outer_id: return

        user = QdUser.objects(domain=domain, source_data_info__outer_id=outer_id).first()
        if not user:
            user_name = tools.get_uuid()
            user = QdUser(domain=domain, user_name=user_name)
            user.source_data_info['outer_id'] = outer_id

        user.set_attrs(mobile=mobile, gender=gender, name=nick_name, dpassword=dpassword)
        user.saveEx()
        return user

    @classmethod
    def _bind_local_aptms(cls, xqx_user, outer_member_room_ids=[]):
        """
        给xqx User绑定房间
        :param xqx_user: T-QdUser, 用户对象
        :param outer_member_room_ids: 北京用户信息中的所有绑定房间ID
        :return:
        """

        from apis.qduser import QdUserNotifyApi
        aptms = Room.objects(domain=domain, source_data_info__outer_id__in=outer_member_room_ids)
        _aptms = Room.objects(domain=domain, residents=xqx_user)

        xqx_user.related_aptms = aptms
        xqx_user.saveEx()

        for aptm in _aptms:
            if aptm not in aptms:
                aptm.residents.remove(xqx_user)
                aptm.save()
                QdUserNotifyApi._notify_user_aptm_change(aptm, [str(xqx_user.id)], op_type="unbind",
                                                         alias=[str(xqx_user.id)])
        for aptm in aptms:
            if xqx_user not in aptm.residents:
                aptm.residents.append(xqx_user)
                if not aptm.talk_contact_phone: aptm.talk_contact_phone = xqx_user.mobile
                aptm.save()
                QdUserNotifyApi._notify_user_aptm_change(aptm, [str(xqx_user.id)], op_type="bind",
                                                         alias=[str(xqx_user.id)])

    def check_service_onoff(self, member_id, services=["cloud_talk", "cloud_alarm"]):
        """
        获取用户是否开通 云对讲/云报警 功能
        :param member_id: T-string, 北京用户编号
        :param services: T-list#string, 检测开通服务列表["cloud_talk", "cloud_alarm"]， 可单选
        :return: data->{"cloud_talk":#bool, "cloud_alarm":#bool}
        """
        result = get_default_result()
        if not services: return result

        user = QdUser.objects(domain=domain, source_data_info__outer_id=member_id).first()
        if "cloud_talk" in services:
            result.setdata("cloud_talk", True if user else False)

        if "cloud_alarm" in services:
            if not user: result.setdata("cloud_alarm", False)
            else:
                agw_count = AlarmGateway.objects(domain=domain, aptm__in=user.related_aptms).count()
                result.setdata("cloud_alarm", True if agw_count else False)

        return result

    def report_comm_event(self, topic, data={}, at=None, eid=None):
        """
        通用服务器事件、通知
        :param topic: T-string, 事件主题 如: /bj/user_bind_aptm
        :param data: T-object, 事件中包涵必要的数据
        :param eid: T-string, 事件id,使用UUID生成的唯一值(可选参数)
        :param at: T-int | float, 时间截(秒) (可选参数)
        :return: data->{}
        """
        result = get_default_result()
        # todo
        return result

    @classmethod
    def _is_aptm_master(cls, member_id, room_id):
        """
        调用北京接口，判断当前用户是为房间管理员
        :param aptm: T-Room
        :return:
        """

        url = CONF.get("domain").get("www.qdingnet.com").get("apis").get("check_role")
        params = dict(memberId=member_id, roomId=room_id)
        flg, msg, res_json = cls._request_bj_api(url, params)

        if not flg:
            log.warning(msg)
            return False

        has_role = res_json.get("data", {}).get("hasRole", False)
        return has_role

    def notify_bj_room_data_change(self, project_id):
        """
        外部调用此接口，通知xqx系统基础数据变更
        :param project_id:
        :return:
        """
        from utils.qd import QDEvent
        result = get_default_result()
        QDEvent("bjqd/notify_bj_room_data_change", data={"project_id": project_id}).broadcast()

        return result

    @classmethod
    def _sync_bj_room_data(cls, project_id):
        """
        同步北京项目基础数据
        :param project_id: T-str
        :return:
        """
        from apis.outer import sync_bj_data as sbd

        xml_file_name = "%s.xml" % project_id
        sbd.get_xml_data(xml_file_name)

    @classmethod
    @rds_api_cache(600, think_session=False)
    def _get_user_avatar_url(cls, member_id):
        """
        调用北京接口，获取用户头像完整的URL
        :param user: T-QdUser
        :return: url
        """

        default_url = "http://avatar.csdn.net/1/D/6/1_crylearner.jpg"
        flg, msg, res_json = cls._load_user_info(member_id)
        if not flg:
            return default_url

        head_img = res_json.get("data", {}).get("userData", {}).get("headImg", "")
        if not head_img: return default_url

        return head_img
