# coding=utf-8
from apis.base import BaseApi
from utils.tools import get_default_result


class AlarmApi(BaseApi):
    '''
    报警通用操作API
    '''

    def get_break_alarms(self, device_sn, pager={}):
        '''

        :param device_sn:
        :param pager:
        :return:
        '''
        result = get_default_result()

        return result
