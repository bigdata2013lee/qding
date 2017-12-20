#coding=utf-8
import base64
import json
import logging
import os

import re
import datetime

from apis.base import BaseApi

from conf.qd_conf import CONF
from models.account import QdUser
from models.aptm import Room
from models.common import ImageCallSnapshot
from models.device import Gate, AioManager
from models.record import CallRecord, GateOpenLockRecord, Dev2AptmCallRecord
from utils.tools import get_default_result
from utils import tools
from utils import qd
from utils.permission import app_user_login_required, common_login_required, wuey_user_login_required, \
    public_dev_login_required

log = logging.getLogger('django')
justalk_log = logging.getLogger('justalk')

class TalkCommonApi(BaseApi):
    """
    千丁App User 相关操作API
    """

    def _get_client(self, user_type, user_id):

        cls_list = [QdUser, Gate, AioManager]
        _cls = None
        for c in cls_list:
            if c.__name__ == user_type:
                _cls = c
                break

        if not _cls: return None

        client = _cls.objects(id=user_id).first()
        return client

    def jusTalk_authorization(self):
        """
        jusTalk 鉴权接口, 提供给justalkcloud.com
        :return:
        """
        log = justalk_log
        result = {}
        body = (self.request.body or b'{}').decode("utf-8")

        body_obj = json.loads(body)
        log.debug(body_obj)

        p = "username:(\w+)-(\w+)@"

        tid = body_obj.get("tid", "")
        cmd = body_obj.get("cmd", "")
        oid = body_obj.get("oid", "")

        body_in = body_obj.get("in", {})

        md5pwd = body_in.get("md5pwd", "")
        random = body_in.get("random", "")
        account = body_in.get("account", "")

        find = re.findall(p, account)

        user_type = find[0][0] if find else ""
        user_id = find[0][1] if find else ""

        if not tid or not user_id or not random:
            log.debug("jusTalk_authorization: fail")
            return dict(tid=tid, ret=False)

        client = self._get_client(user_type, user_id)

        log.debug(client)
        if not client:
            log.debug("jusTalk_authorization: account not found")
            return dict(tid=tid, exception="account-error")

        if tools.md5_str(random + client.dpassword) != md5pwd:
            log.debug("jusTalk_authorization: pwd not match")
            return dict(tid=tid, exception="pwd-error")

        log.debug("jusTalk_authorization: ok")
        result.update(dict(tid=tid, ret=True))
        return result

    def jusTalk_call_state_notification(self):
        """
        获取通话状态通知 提供给justalkcloud.com
        :return:
        """
        log = justalk_log
        result = {}
        body = (self.request.body or b'{}').decode("utf-8")

        body_obj = json.loads(body)
        log.debug(body_obj)

        tid = body_obj.get("tid", "")
        result.update(dict(tid=tid, ret=True))
        return result

    @common_login_required
    def get_user_ids_by_aptm_fuuid(self, aptm_fuuid):
        """
        设备调用此接口获取房间FUUID下，所有住户ID,及房间ID
        :param aptm_fuuid: T-string, 带格式的房间UUID etc: 1-2-3-4-5
        :return: data->{collection:[#str,...], aptm_id:#str, user_type_prefix:#str, talk_contact_phone:#str}
        :notice: 仅限设备端调用
        """

        result = get_default_result()
        result.data_collection = []
        result.data["aptm_id"] = None
        
        dev = self._get_login_device()
        project = dev.project
        aptm_uuid = "".join(["{0:0>3}".format(x) for x in tools.parse_apartment_fuuid(aptm_fuuid) or []])
        if not aptm_uuid:
            return result.setmsg("房间编号错误", 3)

        aptm = Room.objects(project=project, aptm_uuid=aptm_uuid).first()
        if aptm:
            result.data["aptm_id"] = str(aptm.id)
            result.data["user_type_prefix"] = "QdUser-"
            result.data["talk_contact_phone"] = aptm.talk_contact_phone

        for user in aptm.residents if aptm else []:
            result.data_collection.append(str(user.id))

        return result

    @common_login_required
    def gate_get_talk_aios(self):
        """
        门口机获取对讲可呼叫的管理机信息列表
        :return: data->{collection:[{id:str,name:str}]}
        """
        result = get_default_result()
        dev = self._get_login_device()
        project = dev.project

        aios = AioManager.objects(project=project, is_valid=True)
        result.data_collection = []
        for aio in aios:
            result.data_collection.append(aio.outputEx(inculde_fields=["_id", "name"]))

        return result

    @app_user_login_required
    def get_user_pass_gates(self):
        """
        App user 获取有权限通过的门口机列表
        :return: data->{collection:[{project_id:#str, project_name:#str, gates:[#obj]},...]}
        """

        from apis.gate import GateApi
        result = get_default_result()
        user = self._get_login_user()

        result.data_collection = []
        gate_api = GateApi()
        for aptm in user.related_aptms:
            if not aptm:
                log.warning("Not found aptm %s", aptm)
                continue

            project, gates = gate_api._get_pass_gates_for_aptm(aptm)
            item = {"project_id": str(project.id), "project_name": project.name, "gates": [gate.outputEx() for gate in gates]}
            result.data_collection.append(item)

        return result

    @common_login_required
    def set_aptm_contact_phone(self, aptm_id, phone_number=""):
        """
        设置呼叫转接电话
        :param aptm_id: T-string, 房间ID
        :param phone_number: T-string, 转接电话号码
        :return: data->{}
        :notice: 当参数phone_number为空时，取消呼叫转接电话
        """
        result = get_default_result()
        user = self._get_login_user()
        aptm = Room.objects(id=aptm_id).first()

        if not aptm:
            return result.setmsg("设置呼叫转接电话失败", 3)

        if user and isinstance(user, (QdUser,)) and user not in aptm.residents:
            return result.setmsg("非家庭管理员不能操作", 3)

        if phone_number and not re.findall("^1\d{10}$", phone_number):
            return result.setmsg("设置呼叫转接电话失败", 3)

        if not phone_number:
            aptm.talk_contact_phone = ""
            result.setmsg("取消呼叫转接电话完成")
        else:
            aptm.talk_contact_phone = phone_number
            result.setmsg("设置呼叫转接电话完成")

        aptm.saveEx()

        return result

    @common_login_required
    def get_aptm_contact_phone(self, aptm_id):

        """
        获取呼叫转接电话
        :param aptm_id: T-string, 房间ID
        :return: data->{talk_contact_phone:#str}
        """
        result = get_default_result()
        aptm = Room.objects(id=aptm_id).first()
        result.setdata("talk_contact_phone", aptm.talk_contact_phone if aptm else "")
        return result

    def set_aptm_contact_order(self, aptm_id, order_residents=[]):
        """
        调整房间下住户的（对讲接听）顺序
        :param aptm_id: T-string, 房屋ID
        :param order_residents: T-[#str,...], 已经排序的住户列表
        :return:
        """
        result = get_default_result()
        aptm = Room.objects(id=aptm_id).first()

        if not aptm:
            return result.setmsg("指定的房间不存在", 3)

        aptm.order_residents(order_residents=order_residents)

        return result


class CallRecordApi(BaseApi):

    @wuey_user_login_required
    def query_for_wuye(self, phase_no=0, building_no=0, aptm_short_code="", pager={}):

        """
        物业查询通话记录
        :param phase_no: T-int, 期序号
        :param building_no: T-int, 楼栋序号
        :param aptm_short_code: T-string, 房间短码
        :param pager: T-obj, 分页
        :return: data->{collection:[#obj,...]}
        """
        result = get_default_result()
        result.data_collection = []
        user = self._get_login_user()

        project = user.project

        conditions = {"project": project}

        codes = [phase_no, building_no, 0, 0, 0]

        if aptm_short_code:
            codes[3:] = tools.parse_aptm_short_code(aptm_short_code)

        aptm_pattern = tools.parse_codes_to_aptm_uuid_pattern(codes)

        conditions.update({"aptm_uuid": re.compile(aptm_pattern)})

        log.debug("conditions:%s", conditions)
        calls = CallRecord.objects(**conditions).order_by("-created_at")
        result.data = tools.paginate_query_set(calls, pager)

        return result

    @classmethod
    def _add_call_index_snapshot(cls, call_record, base64_file):
        """
        保存通话记录封面图
        :param call_record: T-document, 通话记录
        :param base64_file: T-string, base64 图片
        :return: bool

        :notice: 下载url http(s)://$host/image/call/index_snapshot/$call_id
        """

        if not call_record or not base64_file or not isinstance(base64_file, str):
            return False, ""

        fsize = 0
        try:
            img = base64.standard_b64decode(base64_file)
            fsize = len(img)

        except Exception as e:
            return False, ""

        snapshot = call_record.index_snapshot
        if not snapshot: snapshot = ImageCallSnapshot(project=call_record.project)

        snapshot.base64 = base64_file
        snapshot.fsize = fsize
        snapshot.saveEx()

        call_record.index_snapshot = snapshot
        call_record.saveEx()
        return True, ""




    def add_call_snapshots(self, call_record_id, base64_files=[]):
        """
        添加 通话记录截图
        :param call_record_id: T-string 通话记录ID
        :param base64_files: T-[#string] base64格式的字符串数组
        :return:

        :notice: 文件路径:  /media/snapshot/$call_id/
        """
        result = get_default_result()
        app_home = CONF['app_home']

        call_record = CallRecord.objects(id=call_record_id).first()
        if not call_record or not base64_files or not isinstance(base64_files, list):
            return result.setmsg("上传失败,参数错误", 3)

        img_base = "media/snapshot/%s" % (str(call_record.id))
        rel_img_dir = os.path.join(app_home, img_base)

        log.debug("base path: %s, rel_img_dir:%s", app_home, rel_img_dir)

        os.system("mkdir -p %s" % rel_img_dir)
        file_num = len(base64_files)
        _start = call_record.start_at.timestamp()

        snapshot_infos = []
        for i in range(file_num):
            _f_path = os.path.join(rel_img_dir, "%s.jpg" % i)
            log.debug("file path: %s", _f_path)
            _t_stamp = _start + (call_record.duration / file_num) * i
            _snapshot_at = datetime.datetime.fromtimestamp(_t_stamp)
            snap_item = {"path": _f_path, "at": _snapshot_at}
            snapshot_infos.append(snap_item)

        for base64_data, snap in zip(base64_files, snapshot_infos):
            with open(snap.get("path"), mode="wb+") as f:
                try:
                    img_file_data = base64.standard_b64decode(base64_data)
                    f.write(img_file_data)
                except Exception as e:
                    log.exception(e)

            snap['path'] = snap['path'].replace(app_home, "")

        call_record.snapshots_list = snapshot_infos
        call_record.saveEx()

        return result

    @app_user_login_required
    def app_sync_last_calls(self):
        """
        App 同步最近的通话记录列表
        :return: data->{collection:[#obj]}
        """
        result = get_default_result()
        result.data_collection = []
        user = self._get_login_user()
        before_at = datetime.datetime.now() + datetime.timedelta(days=-7)
        calls = []
        for aptm in user.related_aptms:
            _calls = Dev2AptmCallRecord.objects(project=aptm.project, aptm=aptm, created_at__gte=before_at)
            calls += _calls

        for call in calls:
            result.data_collection.append(call.outputEx())

        return result

    @public_dev_login_required
    def report_dev2dev_call_record(self, to_dev_id, duration=0, is_received=True):
        """
        设备之间相互呼叫(门口机<--->物业机) 上报呼叫通话记录
        :param to_dev_id: T-string, 被叫设备ID
        :param duration: T-int, 通话时长(秒)
        :param is_received: T-boolean, 是否接通
        :return: data->{"call_record_id":#str}
        """

        result = get_default_result()

        return result

    @public_dev_login_required
    def report_dev2aptm_call_record(self, aptm_id, duration=0, is_received=True, recv_user_id="", index_snapshot_base64=""):
        """
        门口机/物业机 上报呼叫家庭通话记录
        :param aptm_id: T-string,房间ID
        :param duration: T-int, 通话时长(秒)
        :param is_received: T-boolean, 是否接通
        :param recv_user_id: T-string, 接口用户ID
        :param index_snapshot_base64: T-string, base64-str, 通话封面图
        :return: data->{"call_record_id":#str}
        """

        result = get_default_result()
        if not duration or duration < 0: duration = 0
        dev = self._get_login_device()

        aptm = Room.objects(id=aptm_id).first()

        now = datetime.datetime.now()
        start_at = now
        end_at = now - datetime.timedelta(seconds=duration)
        call_record = Dev2AptmCallRecord(start_at=start_at, end_at=end_at, duration=duration, is_received=is_received)

        call_record.from_desc = "%s %s" % (dev.cls_desc_name, dev.name)
        call_record.to_desc = aptm.get_aptm_short_name()

        call_record.set_attrs(domain=aptm.domain, project=dev.project, aptm=aptm, aptm_uuid=aptm.aptm_uuid)
        call_record.set_attrs(dev_id=str(dev.id), dev_type=dev.__class__.__name__, dev_uuid=dev.dev_uuid)

        call_record.saveEx()

        # 保存通话封面
        if index_snapshot_base64:
            CallRecordApi._add_call_index_snapshot(call_record, index_snapshot_base64)

        result.setdata('call_record_id', str(call_record.id))

        # 广播未接来电事件
        if not is_received:
            pass
            # qd.QDEvent("missed_call", project_id=aptm.project.id, data=call_record.outputEx()).broadcast()

        return result

    @public_dev_login_required
    def aio_get_call_record(self,  pager={}):
        """
        获取本项目所有物业机的通话记录
        :param pager: T-obj, 分页信息
        :return: data->{collection:[....]}
        """
        result = get_default_result()
        result.data_collection = []
        return result


class GateOpenLockRecordApi(BaseApi):

    @wuey_user_login_required
    def query_for_wuye(self, cls_name="", pager={}):
        """
        物业查询开锁记录
        :param cls_name: T-string, 开锁记录类型 可选值 "ResidentOpenLockRecord" | "NotResidentOpenLockRecord"
        :param pager: T-#obj, 分页
        :return: data->{collection:[#obj,...]}
        """
        result = get_default_result()
        user = self._get_login_user()

        project = user.project
        conditions = {"project": project}

        if cls_name:
            conditions.update({"_cls": "GateOpenLockRecord.%s" % cls_name})

        recoreds = GateOpenLockRecord.objects(**conditions).order_by('-created_at')

        result.data = tools.paginate_query_set(recoreds, pager)

        return result


