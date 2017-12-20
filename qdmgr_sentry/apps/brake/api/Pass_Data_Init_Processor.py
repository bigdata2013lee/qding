# -*- coding:utf8 -*-
from apps.brake.api.Pass_Data_Common_Processor import Pass_Data_Common_Processor


class Pass_Data_Init_Processor(Pass_Data_Common_Processor):
    def hand_request(self, brake_pass, result, apartment, brake_obj, sentry_visitor):
        if brake_pass.get_unique_pass(created_time=brake_pass.created_time, mac=brake_obj.mac):
            result['msg'] = 'Pass_Data_Init_Processor: 同一闸机同一秒只允许存在一条通行记录'
            result['data']['flag'] = 'N'
        else:
            brake_pass.save()
        if self.processor is not None and result['data']['flag'] == 'Y':
            self.processor.hand_request(brake_pass, result, apartment, brake_obj, sentry_visitor)
