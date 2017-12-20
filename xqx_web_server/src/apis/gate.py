# coding=utf-8
import logging
import datetime
import re

from apis.base import BaseApi
from models.account import QdUser
from models.aptm import Room, Project
from models.common import AccessCard
from models.device import Gate, UnitGate, FenceGate
from models.record import ResidentOpenLockRecord, NotResidentOpenLockRecord
from utils import misc
from utils import qd
from utils import tools
from utils.qd import QdRds
from utils.tools import paginate_query_set, rds_api_cache
from utils.tools import get_default_result
from utils.permission import common_login_required, public_dev_login_required

log = logging.getLogger('django')

class GateApi(BaseApi):
    """
    门口机相关操作API
    """

    def _get_pass_gates_for_aptm(self, aptm):

        project = aptm.project

        gates = []

        aptm_codes = tools.parse_apartment_uuid(aptm.aptm_uuid)

        unit_gate_uuid_pattern = re.compile(r"\d+-{0}-{1}-{2}-\d+-\d+-\d+".format(*aptm_codes))
        unit_gates = UnitGate.objects(project=project, dev_uuid=unit_gate_uuid_pattern)

        fen_gate_uuid_pattern = re.compile(r"\d+-{0}-\d+-\d+-\d+-\d+-\d+".format(*aptm_codes))
        fen_gates = FenceGate.objects(project=project, dev_uuid=fen_gate_uuid_pattern)

        for gate in unit_gates: gates.append(gate)
        for gate in fen_gates: gates.append(gate)

        return project, gates


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

        if not dev_codes or dev_codes[0] not in [20, 22]:
            log.warning("register_device->设备UUID错误, dev_uuid:%s", dev_uuid)
            return result.setmsg("设备UUID错误", 3)

        project = Project.objects(code=project_code).first()
        dev = Gate.objects(sn=sn).first()

        if not project:
            log.warning("register_device->Can not find Project by code:%s", project_code)
            return result.setmsg("Can not find Project by code:%s" % project_code, 3)

        if not dev:
            dev = dev_cls.create_inst(dev_uuid)
            dev.sn = sn
            dev.saveEx()

        # 设备存在，但UUID变化了，此设备需要删除后重建立，但要保留原objectid
        elif dev and dev.dev_uuid != dev_uuid:
            dev_id = dev.id
            dev.delete()

            dev = dev_cls.create_inst(dev_uuid)
            dev.sn = sn
            dev.id = dev_id

        dev.set_attrs(domain=project.domain, project=project)
        dev.dpassword = tools.md5_str(tools.get_uuid())
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
        dev = Gate.objects(id=device_id).first()
        if not dev:
            return result.setmsg("登陆失败，设备不存在", 3)

        if dev.dpassword != login_token:
            return result.setmsg("登陆失败，Token失效", 3)

        self._set_logined("gate", dev.id)
        return result

    @common_login_required
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
        门口机上报心跳
        :param device_id: T-string,设备ID
        :param rom_version: T-string,ROM版本
        :param app_version: T-string,主应用版本
        :return: data->{}
        """
        result = get_default_result()
        dev = Gate.objects(id=device_id).first()
        if not dev:
            return result.setmsg("Can not found device:%s" % device_id, 3)

        ostatus = dev.heartbeat.get("status", "down")

        dev.versions = {"rom_version": rom_version, "app_version": app_version}
        dev.heartbeat = {"at": datetime.datetime.now(), "status": 'up'}
        dev.saveEx()

        tools.set_dev_heartbeat_ex_timer('gate', dev.id, ex=60 * 15)
        if ostatus != "up":
            evt_data = dict(dev=dev.outputEx(), status="up", dev_type=dev.__class__.__name__)
            qd.QDEvent("device_heartbeat_status_change", data=evt_data).broadcast()

        return result

    def _make_deal_funcs_for_open_gate_ways(self, project, dev, open_way):
        """创建多种开锁方式"""

        def _init_rolr(aptm):
            opener_detail = aptm.get_aptm_short_name()
            rolr = ResidentOpenLockRecord(open_way=open_way, gate_uuid=dev.dev_uuid, gate_name=dev.get_title(),
                                          opener_detail=opener_detail)

            rolr.set_attrs(domain=project.domain, project=project, aptm=aptm, aptm_uuid=aptm.aptm_uuid)
            return rolr

        def _init_not_rolr(opener_detail):
            not_rolr = NotResidentOpenLockRecord(domain=project.domain, project=project, open_way=open_way,
                                                 gate_uuid=dev.dev_uuid, gate_name=dev.get_title(),
                                                 opener_detail=opener_detail)

            return not_rolr

        def __card(infos):

            card_no = infos.get("card", "")
            card = AccessCard.objects(project=project, card_no=card_no).first()
            if not card:
                return False, "不存在的卡号:%s" % card_no

            card_type_name = dict(AccessCard.TYPE_CHOICES).get(card.card_type, "")

            if card.card_type == "resident":
                aptm = Room.objects(project=project, aptm_uuid=card.aptm_uuid).first()
                if not aptm: return False, "卡号未正确关联房间"

                rolr = _init_rolr(aptm)
                aptm_name = aptm.get_aptm_short_name()
                opener_detail = "%s:%s (%s)" % (card_type_name, card_no, aptm_name)
                rolr.opener_detail = opener_detail
                rolr.saveEx()
                return True, ""

            elif card.card_type == ['manager', 'worker']:
                opener_detail = "%s:%s (%s)" % (card_type_name, card_no, card.owner_name)
                not_rolr = _init_not_rolr(opener_detail)
                not_rolr.saveEx()
                return True, ""

            return False, "不支持的访问卡类型:%s" % card.card_type

        def __aptm_call(infos):
            aptm_id = infos.get("aptm_id", "")
            user_id = infos.get("user_id", "")

            aptm = Room.objects(id=aptm_id).first()

            if not aptm:
                log.warning("report_open_lock -> 房间不存在aptm_id:%s" % aptm_id)
                return False, "房间不存在aptm_id:%s" % aptm_id

            rolr = _init_rolr(aptm)
            rolr.saveEx()

            return True, ""

        def __call_phone(infos):
            aptm_id = infos.get("aptm_id", "")

            aptm = Room.objects(id=aptm_id).first()

            if not aptm:
                log.warning("report_open_lock -> 房间不存在aptm_id:%s" % aptm_id)
                return False, "房间不存在aptm_id:%s" % aptm_id

            rolr = _init_rolr(aptm)
            rolr.saveEx()

            return True, ""

        def __resident_pwd(infos):

            aptm_id = infos.get("aptm_id", "")
            user_id = infos.get("user_id", "")
            aptm = Room.objects(id=aptm_id).first()
            # user = QdUser.objects(id=user_id).first()

            if not aptm:
                log.warning("report_open_lock -> 房间不存在aptm_id:%s" % aptm_id)
                return False, "房间不存在aptm_id:%s" % aptm_id

            rolr = _init_rolr(aptm)
            rolr.saveEx()

            return True, ""

        def __gate_pwd(infos):
            pwd = infos.get("pwd", "")
            opener_detail = "物业人员"
            not_rolr = _init_not_rolr(opener_detail)
            not_rolr.saveEx()

            return True, ""

        def __app_remote(infos):

            user_id = infos.get("user_id", "")
            user = QdUser.objects(id=user_id).first()
            if not user or not user.related_aptms:
                log.debug("User:%s not exist or not related_aptms", user_id)
                return False, "User:%s not exist or not related_aptms" % user_id

            find_aptm = None

            # 查找能通过此门的房间
            for aptm in user.related_aptms:
                if dev.project != aptm.project: continue
                codes = tools.parse_device_uuid(dev.dev_uuid)[1:4]
                aptm_uuid = aptm.aptm_uuid

                p = tools.parse_codes_to_aptm_uuid_pattern(codes)
                find = re.findall(p, aptm_uuid)
                if not find: continue

                find_aptm = aptm
                break

            if not find_aptm:
                return False, "Not found aptm"

            rolr = _init_rolr(aptm)
            rolr.saveEx()

            return True, ""

        return __card, __aptm_call, __call_phone, __resident_pwd, __gate_pwd, __app_remote

    @common_login_required
    def report_open_lock(self, open_way="aptm_call", opener_infos={}):
        """
        根据不同的开锁方式及开锁信息，创建一个开锁记录
        :param open_way: T-string, 开锁方式 可选值 card|gate_pwd|resident_pwd|aptm_call|call_phone|app_remote|aio_call
        :param opener_infos: T-obj, 开锁者扩展
        :return: data->{}

        :notice:
        open_way=card 刷卡开锁, 需要区分不同的类型的访问卡
            opener_infos={card:#str}

        open_way=aptm_call 呼叫家庭开锁
                opener_infos={aptm_id:#str, user_id:#str}

        open_way=call_phone 呼叫家庭电话开锁
                opener_infos={aptm_id:#str}

        open_way=gate_pwd 门口机固定密码开锁
            opener_infos={pwd:#str}

        open_way=resident_pwd 住户密码开锁
            opener_infos={pwd:#str, user_id:#str, aptm_id:#str}

        open_way=app_remote app开锁
            opener_infos={user_id:#str}

        open_way=aio_call 呼叫物业机开锁
            opener_infos={aio_id:#str}

        """

        result = get_default_result()
        dev = self._get_login_device()
        project = dev.project
        Enum = misc.GateOpenWaysEnum

        log.debug("report_open_lock params: %s, %s", open_way, opener_infos)

        if open_way not in Enum.get_vals():
            return result.setmsg("不支持的开门类型", 3)

        funcs = self._make_deal_funcs_for_open_gate_ways(project, dev, open_way)
        ways = (Enum.card, Enum.aptm_call, Enum.call_phone, Enum.resident_pwd, Enum.gate_pwd, Enum.app_remote)
        ways_funcs = dict(zip(ways, funcs))

        fg, msg = ways_funcs.get(open_way)(opener_infos)
        return result.setmsg(msg, 0 if fg else 3)

    @common_login_required
    def list_project_gates(self, project_id, dev_type="", heartbeat_status="", phase_no=0, building_no=0, pager={}):
        """
        查询项目中的门口机设备
        :param project_id: T-string, 项目ID
        :param dev_type: T-string, 设备类型
        :param heartbeat_status: T-string, 心跳状态 up|down
        :param phase_no: T-int, 组团序号
        :param building_no: T-int, 楼栋序号
        :param pager: T-obj, 分页
        :return: data->{collection:[#obj,...]}
        """

        result = get_default_result()
        devices = Gate.objects(project=project_id)
        conditions = {}

        if dev_type:
            conditions.update({"_cls": dev_type})

        if heartbeat_status:
            conditions.update({"heartbeat.status": heartbeat_status})

        if phase_no or building_no:
            p = "^\d+"
            p += "-%d" % phase_no if phase_no else "-\d+"
            p += "-%d" % building_no if building_no else "-\d+"

            conditions.update({"dev_uuid": {"$regex": p}})

        devices = devices.filter(__raw__=conditions)
        result.data = paginate_query_set(devices, pager=pager)

        return result

    @common_login_required
    def sync_access_cards(self):
        """
        门口机同步卡数据
        :return: data->{collection:[#obj,...]}
        """

        result = get_default_result()

        gate = self._get_login_device()
        project = gate.project

        codes = tools.parse_device_uuid(gate.dev_uuid)
        if not codes: return result.setmsg("门口机DEV_UUID错误", 3)

        aptm_pattern_str = tools.parse_codes_to_aptm_uuid_pattern(codes[1:4])

        resident_cards = self._sync_cards(str(project.id), aptm_pattern_str)
        other_cards = self._sync_cards(str(project.id))

        result.data_collection.extend(resident_cards)
        result.data_collection.extend(other_cards)

        return result

    @rds_api_cache(ex=3600*24*7, think_session=False, mgr_key="args[1]")
    def _sync_cards(self, project_id, aptm_pattern_str=""):
        """
        缓存模式的卡同步查询
        当 aptm_pattern_str 不为空时，只查询物业卡及工作卡
        当 aptm_pattern_str 为空时，只查询住户卡

        :param project_id: T-string, 项目ID
        :param aptm_pattern_str: T-string, 正则表达式字符串
        :return: T-[#obj, ...]
        """
        cards = AccessCard.objects(project=project_id, is_valid=True)
        if aptm_pattern_str:
            cards = cards.filter(__raw__=dict(card_type="resident", aptm_uuid={"$regex": aptm_pattern_str}))
        else:
            cards = cards.filter(card_type__in=["manager", "worker"])

        cards_collection = []
        for card in cards:
            o = card.outputEx(exculde_fields=["created_at", "updated_at", "is_valid", "owner_name", "project", "name"])
            cards_collection.append(o)

        return cards_collection

    @classmethod
    def _remove_sync_cards_cache(cls, project_id):

        rds = QdRds.get_redis()
        keys = rds.keys("api_cache_%s._sync_cards[mgr_key-%s]*" % (cls.__name__, project_id))
        if not keys: return 

        rds.delete(*keys)

    @common_login_required
    def wy_set_pass_password(self, gate_id, pwd=""):
        """
        设置门口机通行的密码(用于物业人员通行)
        :param gate_id: T-string, 门口机ID
        :param pwd: T-string, 4位密码， 当密码为空时，意味着取消密码
        :return: data->{}
        """
        result = get_default_result()
        user = self._get_login_user()

        if pwd and not re.findall("^\d{4}$", pwd):
            return result.setmsg("设置的密码格式错误", 3)

        gate = Gate.objects(id=gate_id).first()
        if not gate: return result.setmsg("门口机设备不存在", 3)

        old_pwd = gate.pass_password
        gate.pass_password = pwd
        gate.saveEx()

        if old_pwd != pwd:
            extras = {"msg_type": "gate/sync_pass_password"}
            tools.send_push_message(extras=extras, alias=["gate:%s" % gate_id])

        return result

    @common_login_required
    def gate_sync_pass_password(self):
        """
        门口机同步物业通行密码
        :return: data -> {"pwd":#str}
        """
        result = get_default_result()
        gate = self._get_login_device()
        result.data['pwd'] = gate.pass_password if gate else ""
        return result

    @public_dev_login_required
    def aio_get_gates(self, dev_type="", heartbeat_status=""):
        """
        管理机获取当前社区的所有门口机列表
        :return: data->{collection:[....]}
        """
        result = get_default_result()
        dev = self._get_login_device()

        conditions = {}

        if dev_type:
            conditions.update({"_cls": dev_type})

        if heartbeat_status:
            conditions.update({"heartbeat__status": heartbeat_status})

        gates = Gate.objects(is_valid=True, project=dev.project, **conditions)

        result.data_collection_output(gates, inculde_fields=["_id", "name", "label", "heartbeat", "_cls"])

        return result













