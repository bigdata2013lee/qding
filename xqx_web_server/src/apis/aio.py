#coding=utf8
import logging

import datetime

from apis.base import BaseApi
from models.aptm import Project
from models.device import Gate, AioManager
from utils import qd
from utils import tools
from utils.permission import common_login_required, public_dev_login_required
from utils.tools import get_default_result, paginate_query_set

log = logging.getLogger('django')

class AioDeviceApi(BaseApi):

    def register_device(self, project_code, dev_uuid, sn):
        """
        设备注册
        :param project_code: T-string, 社区项目编号
        :param dev_uuid: T-string, 设备编号
        :param sn: T-string, 设备SN
        :return: data->{project_id:#str, device_id:#str, login_token:#str}
        :notice: 此接口应在设备第一次注册时，或在开机启动时调用，允许重复注册，每次注册时login_token会变化
        """
        result = get_default_result()

        dev_codes = tools.parse_device_uuid(dev_uuid)
        dev_cls = tools.match_device_cls_by_uuid(dev_uuid)

        if not dev_codes or dev_codes[0] not in [30]:
            log.warning("register_device->设备UUID错误, dev_uuid:%s", dev_uuid)
            return result.setmsg("设备UUID错误", 3)

        project = Project.objects(code=project_code).first()
        dev = AioManager.objects(sn=sn).first()

        if not project:
            log.warning("register_device->Can not find Project by code:%s", project_code)
            return result.setmsg("Can not find Project by code:%s" % project_code, 3)

        if not dev:
            dev = dev_cls.create_inst(dev_uuid)
            dev.set_attrs(project=project, domain=project.domain, sn=sn)
            dev.saveEx()

        dev.dpassword = tools.md5_str(tools.get_uuid())
        dev.project = project
        dev.saveEx()

        result.data['register'] = {"project_id": str(project.id), "device_id": str(dev.id), "login_token": dev.dpassword}

        return result


    def device_login(self, device_id, login_token):
        """
        设备登陆
        :param device_id: T-string,设备ID
        :param login_token: T-string, 登陆证书
        :return: data->{}
        """
        result = get_default_result()
        dev = AioManager.objects(id=device_id).first()
        if not dev:
            return result.setmsg("登陆失败，设备不存在", 3)

        if dev.dpassword != login_token:
            return result.setmsg("登陆失败，Token失效", 3)

        self._set_logined("aio", dev.id)
        return result


    @public_dev_login_required
    def me(self):
        """
        获取当登陆设备信息
        :return:data->{device:#obj}
        """
        result = get_default_result()
        dev = self._get_login_user()
        result.data['device'] = dev.outputEx()
        return result


    @public_dev_login_required
    def report_heartbeat(self, device_id, rom_version="", app_version=""):
        """
        物业管理机上报心跳
        :param device_id: T-string,设备ID
        :param rom_version: T-string,ROM版本
        :param app_version: T-string,主应用版本
        :return: data->{}
        """
        result = get_default_result()
        dev = AioManager.objects(id=device_id).first()
        if not dev:
            return result.setmsg("Can not found device:%s" % device_id)

        ostatus = dev.heartbeat.get("status", "down")

        dev.versions = {"rom_version": rom_version, "app_version": app_version}
        dev.heartbeat = {"at": datetime.datetime.now(), "status": 'up'}
        dev.saveEx()

        tools.set_dev_heartbeat_ex_timer('aio', dev.id, ex=60 * 15)
        if ostatus != "up":
            evt_data = dict(dev=dev, status="up", dev_type=AioManager.__name__)
            qd.QDEvent("device_heartbeat_status_change", data=evt_data).broadcast()

        return result


    @common_login_required
    def list_project_aios(self, project_id, pager={}):
        """
        查询项目中的物业管理机设备
        :param project_id: T-string, 项目ID
        :param pager: T-obj, 分页
        :return: data->{collection:[#obj,...]}
        """

        result = get_default_result()
        devices = AioManager.objects(project=project_id)

        result.data = paginate_query_set(devices, pager=pager)

        return result
