#coding=utf8
from apis.advertising import AdvApi
from apis.agw import AGWDeviceApi, AlarmApi, AGWDeviceQueryApi, RecordApi
from apis.aio import AioDeviceApi
from apis.application import ApplicationApi
from apis.aptm import AptmManageApi, AptmImportExportApi
from apis.aptm import AptmQueryApi
from apis.card import AccessCardApi, ImportExportCardApi
from apis.gate import GateApi
from apis.gate_pass import GatePasswordPassApi
from apis.mgr import MgrUserApi
from apis.outer.bjqd import BjQdingApi

from apis.pcity import PCityApi
from apis.projectmgr import ProjectMgrApi
from apis.qduser import QdUserApi, QdUserQRCodeApi
from apis.statistic import StatisticApi
from apis.talk import TalkCommonApi, CallRecordApi, GateOpenLockRecordApi
from apis.test import JsonApi
from apis.upgrade import AgwUpgradeApi, ComponentUpgradeApi
from apis.wuye import WuyeUserApi

api_map = {
    "pcity.PCityApi": PCityApi,
    "aptm.AptmManageApi": AptmManageApi,
    "aptm.AptmQueryApi": AptmQueryApi,
    "aptm.AptmImportExportApi": AptmImportExportApi,
    "projectmgr.ProjectMgrApi": ProjectMgrApi,
    "agw.AGWDeviceApi": AGWDeviceApi,
    "agw.AGWDeviceQueryApi": AGWDeviceQueryApi,
    "agw.AlarmApi": AlarmApi,
    "agw.RecordApi": RecordApi,
    "qduser.QdUserApi": QdUserApi,
    "qduser.QdUserQRCodeApi": QdUserQRCodeApi,
    "wuye.WuyeUserApi": WuyeUserApi,
    "mgr.MgrUserApi": MgrUserApi,
    "qdtalk.TalkCommonApi": TalkCommonApi,
    "qdtalk.CallRecordApi": CallRecordApi,
    "qdtalk.GateOpenLockRecordApi": GateOpenLockRecordApi,
    "gate.GateApi": GateApi,
    "aio.AioDeviceApi": AioDeviceApi,
    "upgrade.AgwUpgradeApi": AgwUpgradeApi,
    "card.AccessCardApi": AccessCardApi,
    "card.ImportExportCardApi": ImportExportCardApi,
    "upgrade.ComponentUpgradeApi": ComponentUpgradeApi,
    "gate_pass.GatePasswordPassApi": GatePasswordPassApi,
    "application.ApplicationApi": ApplicationApi,
    "statistic.StatisticApi": StatisticApi,
    "advertising.AdvApi": AdvApi,
    "bjqd.BjQdingApi": BjQdingApi,
    "test.JsonApi": JsonApi,
}