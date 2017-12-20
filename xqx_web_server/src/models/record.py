#coding=utf-8
from mongoengine import *

from models.aptm import Project
from models.base import QdModelMixin

__doc__ = """
记录与通知
"""


class AlarmRecord(QdModelMixin, Document):

    """
    报警记录
    """
    domain = StringField(default="sz.qdingnet.com")
    project = ReferenceField('Project')  # 项目
    aptm = ReferenceField('Room')  # 房间

    aptm_uuid = StringField(default="000" * 5)  # 房间UUID

    aptm_name = StringField(default="")  # 房间名
    aptm_pre_names = ListField(default=["", "", ""])  # 房间 前缀名project_name, phase_name, building_name

    device = ReferenceField('AlarmGateway')  # 设备
    alarm_id = IntField(default=0)  # 报警器端口
    alarm_type = IntField(default=0)  # 报警类型
    alarm_type_name = StringField(default="")  # 报警类型标题
    deal_status = StringField(default="undealed")  # 处理状态 undealed-未处理  dealed-未处理
    deal_desc = StringField(default="")  # 处理备注

    meta = {
        "strict": False, 'index_background': True,
        "indexes": [
            "domain", "project", "aptm", "$aptm_uuid"
        ]
    }


class WarningRecord(QdModelMixin, Document):

    """
    警告记录
    """
    domain = StringField(default="sz.qdingnet.com")
    project = ReferenceField('Project')  # 项目
    aptm = ReferenceField('Room')  # 房间

    aptm_uuid = StringField(default="0000000000")  # 房间FUUID

    aptm_name = StringField(default="")  # 房间名
    aptm_pre_names = ListField(default=["", "", ""])  # 房间 前缀名project_name, phase_name, building_name

    device = ReferenceField('AlarmGateway')  # 设备
    alarm_id = IntField(default=0)  # 报警器端口
    alarm_type = IntField(default=0)  # 报警类型
    alarm_type_name = StringField(default="")  # 报警类型标题

    meta = {
        "strict": False, 'index_background': True,
        "indexes": [
            "domain", "project", "aptm", "$aptm_uuid"
        ]
    }


class AgwOffLineNotice(QdModelMixin, Document):
    """
    网关设备离线通知
    """
    domain = StringField(default="sz.qdingnet.com")
    project = ReferenceField('Project')  # 项目
    aptm = ReferenceField('Room')
    device = ReferenceField('AlarmGateway')

    meta = {
        "strict": False, 'index_background': True,
        "indexes": [
            "domain", "project", "aptm", "device"
        ]
    }


class AgwBcfNotice(QdModelMixin, Document):
    """
    布撤操作通知
    """
    domain = StringField(default="sz.qdingnet.com")
    project = ReferenceField('Project')  # 项目
    aptm = ReferenceField('Room')
    device = ReferenceField('AlarmGateway')

    op_enable = BooleanField(default=True)  # 布撤操作

    op_user_id_desc = StringField(default="")  # 操作者类型描述及ID 如: QdUser:84564564564

    meta = {
        "strict": False, 'index_background': True,
        "indexes": [
            "domain", "project", "aptm", "device"
        ]
    }


class CallRecord(QdModelMixin, Document):
    """ 通话记录
    """
    domain = StringField(default="sz.qdingnet.com")
    project = ReferenceField('Project')  # 项目

    start_at = DateTimeField()    # 接通时间
    end_at = DateTimeField()      # 挂断时间
    duration = IntField(default=0)       # 通话时长
    is_received = BooleanField(default=True)    # 对方是否接通

    from_desc = StringField(default="")   # 拨号方-通话人描述信息
    to_desc = StringField(default="")     # 收听方-通话人描述信息
    index_snapshot = ReferenceField('ImageCallSnapshot')  # 通话封面图

    meta = {
        'allow_inheritance': True, "strict": False, 'index_background': True,
        "indexes": [
            "domain", "project", "-created_at"
        ]
    }


class Dev2AptmCallRecord(CallRecord):
    """
    设备端呼入家庭,门口机/管理机呼入家庭
    """
    domain = StringField(default="sz.qdingnet.com")
    dev_type = StringField(default="")
    dev_id = StringField(default="")
    dev_uuid = StringField(default="")

    aptm = ReferenceField('Room')
    aptm_uuid = StringField(default="")

    snapshots_list = ListField(default=[])  # 通话截屏列表, {"path": "xxx/xxx/", "at": 时间戳(平均计算)}

    meta = {
        'allow_inheritance': True, "strict": False, 'index_background': True,
        "indexes": [
            "domain", "project", "aptm_uuid", "$aptm_uuid", "-created_at"
        ]
    }


class GateOpenLockRecord(QdModelMixin, Document):
    """
    门口机通行记录
    """
    domain = StringField(default="sz.qdingnet.com")
    project = ReferenceField("Project")

    gate_uuid = StringField(default="")
    gate_name = StringField(default="")

    open_way = StringField(default="")  # 开锁方式 card|gate_pwd|resident_pwd|aptm_call|aio_call
    opener_detail = StringField(default="")  # 开锁人详情备注 设备描述, 持卡人信息
    opener_extras = DictField(default={})  # 开锁人扩展信息

    meta = {
        'allow_inheritance': True, "strict": False, 'index_background': True,
        "indexes": [
            "domain", "project", "open_way", "-created_at"
        ]
    }


class ResidentOpenLockRecord(GateOpenLockRecord):
    """
    住户开锁
    """
    meta = {'allow_inheritance': True, "strict": False}
    aptm = ReferenceField("Room")
    aptm_uuid = StringField(default="")


class NotResidentOpenLockRecord(GateOpenLockRecord):
    """
    非住户开锁
    """
    meta = {'allow_inheritance': True, "strict": False}
