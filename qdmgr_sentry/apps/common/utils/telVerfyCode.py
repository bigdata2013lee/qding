# coding=utf-8

import random
import time
import re
import urllib.parse
from urllib.request import Request, urlopen
from settings.const import CONST

maxLive = 120  # 有效期/秒
msgTpl_01 = "您正在申请免费注册XXX，手机验证码 %s ,如果您有任何问题，请联系4006-3525-00 【XXX科技】"


def createPhoneCode(session):
    """
    创建手机验证码
    @param session: http session
    @return: 验证码
    @note: 生成6位的随机数，并把生成的时间及随机码设置在http session中
    """
    chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    x = [random.choice(chars) for i in range(6)]
    verifyCode = "".join(x)
    session["phoneVerifyCode"] = {"time": int(time.time()), "code": verifyCode}
    return verifyCode


def checkPhoneVerifyCode(session, verifyCode):
    """
    检查验证码是否有效
    @param session: http session
    @param verifyCode: 验证码
    @return: True|False
    @note: 验证码在http session存在，且没过期
    """
    codeObj = session.get("phoneVerifyCode", None)
    if not codeObj: return False
    if (time.time() - maxLive) > codeObj.get("time", 0): return False
    code = codeObj.get("code", "")
    if not code: return False
    if code != verifyCode: return False

    return True


def checkLastCodeLive(session):
    """检测最后的验证码是否已经过期,此方法可用于控制频繁发送"""
    codeObj = session.get("phoneVerifyCode", None)
    if not codeObj: return False
    if (time.time() - maxLive) > codeObj.get("time", 0): return False
    return True


def sendTelMsg(msg, phoneID, smsGateNum=2):
    """
    通过短信网关，发送手机短信
    @note: 默认通过第二个短信网关发送出去，第二短信网关是公司最后一个购买的网关
    """
    gates = {"1": _sendTelMsgFromSMSGate1, "2": _sendTelMsgFromSMSGate2}
    return gates.get("%s" % smsGateNum)(msg, phoneID)


def _postUrl(url, data={}):
    """
    向短信网关提交Post数据
    """
    data = urllib.parse.urlencode(data)
    headers = {'Content-Type': "application/x-www-form-urlencoded"}
    req = Request(url, data.encode("utf8"), headers)
    respone = urlopen(req)
    res = respone.read()
    return res


def _sendTelMsgFromSMSGate1(msg, phoneID):
    "网关1发送"
    smsGateUrl = CONST['smsGateUrl']
    params = {"zh": "网脊运维通", "mm": "netbase123", "hm": phoneID, "nr": msg, "sms_type": 42}
    res = _postUrl(smsGateUrl, params)
    ret = re.findall(r"0:", res)
    if ret: return "ok"


def _sendTelMsgFromSMSGate2(msg, phoneID):
    "网关2发送"
    # action=send&userid=&account=账号&password=密码&mobile=15023239810,13527576163&content=内容&sendTime=&extno=
    smsGateUrl = CONST['smsGate']['url']
    params = {"action": "send", "userid": "", "account": "szzd0003", "password": "123456", "mobile": phoneID,
              "content": msg, "sendTime": "", "extno": ""}
    res = _postUrl(smsGateUrl, params).decode('utf8')
    ret = re.findall(r"<returnstatus>Success</returnstatus>", res)
    if ret: return "ok"
    return "error"


if __name__ == "__main__":
    vcode = createPhoneCode({})
    msg = msgTpl_01 % vcode
