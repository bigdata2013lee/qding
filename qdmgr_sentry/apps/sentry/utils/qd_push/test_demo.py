#!/usr/bin/env python
# encoding: utf-8

import json
from apps.sentry.utils.qd_push import PushMsg

class visitor_msg:
    def __init__(self):
        self.province = ''
        self.city = ''
        self.community = ''
        self.name = ''
        self.sex = ''
        self.reason = ''
        self.dest_room = ''
        self.valid_date = ''
        self.valid_times = 0
        self.cardID = 0
        self.sum_of_visitors = 0

    def GetMsgObject(self):
        message = {}
        message['province'] = self.province
        message['city'] = self.city
        message['community'] = self.community
        message['name'] = self.name
        message['sex'] = self.sex
        message['reason'] = self.reason
        message['dest_room'] = self.dest_room
        message['valid_date'] = self.valid_date
        message['valid_times'] = self.valid_times
        message['cardID'] = self.cardID
        message['sum_of_visitors'] = self.sum_of_visitors
        return message


def ttPush():
    msg = visitor_msg();
    msg.province = '广东'
    msg.city = '深圳'
    msg.community = '海天花园'
    msg.name = '胡涛'
    msg.sex = '男'
    msg.reason = '访友'
    msg.dest_room = '2栋1单元402'
    msg.valid_date = '2015-03-20'
    msg.valid_times = '1'
    msg.cardID = '411521198810136413'
    msg.sum_of_visitors = '1'
    json_str = json.dumps(msg.GetMsgObject())
#     push_str=json.dumps({"floor": "1", "id": 96, "province": "\u9655\u897f", "start_time": 1427040000000, "end_time": 1427126353920, "type": "visitation", "status": "new", "community": "\u897f\u5b89\u7d2b\u90fd\u57ce-\u7d2b\u90fd\u57ce", "unit": "1", "index": "209,117,11,239,120,52,108,74,236,34,210,81,193,20,207,126,240,52,230", "city": "\u897f\u5b89", "build": "1\u5e62", "room": "XAzdc1-1-10101", "reason": "\u670b\u53cb\u6765\u8bbf", "gender": "", "name": "APP"})
    push_str=json.dumps({"id":"3","type":"n","title":"开盘了","content":"家准备好子弹，准备开仓","province":"陕西","city":"西安","community":"西安紫都城-紫都城"})
    PushMsg(push_str,'test')
