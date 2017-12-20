# -*- coding: utf-8 -*-
import json
import time
import traceback
from apps.common.utils import qd_result, validate
from apps.common.utils.view_tools import jsonResponse
from apps.common.utils.sentry_date import get_day_datetime, get_datetime_by_timestamp
from apps.sentry.classes.Sentry_Visitor import Sentry_Visitor


class Sentry_Visitor_Api(object):
    """
    @note: 访客的相关操作
    """

    @jsonResponse()
    def get_visitor_list(self, province=None, city=None, project=None, page_size=0, page_no=0, coming="",
                         start_time=None, end_time=None):
        """
        @note: 用途：获取小区的访客记录
        @note: 访问url： /sentry_api/Sentry_Visitor_Api/get_visitor_list/1/
        @note: 测试demo: {province:"重庆",city:"重庆",community:"观山水"}
        @param province: 省份
        @param city: 城市
        @param project: 小区
        @param page_size: 每页的数目
        @param page_no: 具体哪一页
        @param coming: 是否来了，0-未来访,1-已来访
        @param start_time: 开始时间,10位时间戳
        @param end_time: 结束时间,10位的时间戳        
        @return: {'err': 0, 'msg': '', 'log': '', 'data': {'flag':'Y','pass_list':[],'pagination':{'page_no':1,'page_size':50,'total_count':100}}}
        """
        try:
            result = qd_result.get_default_result()
            validate_page_flag, validate_page_str = validate.validate_pagination(page_size, page_no)
            if not validate_page_flag:
                result['msg'] = validate_page_str
                result['data']['flag'] = 'N'
                return result
            start_time_flag, start_time_str = validate.validate_timestamp(str(start_time), "start_time")
            end_time_flag, end_time_str = validate.validate_timestamp(str(end_time), "end_time")
            if start_time and end_time and not (start_time_flag or end_time_flag):
                result['msg'] = start_time_str, end_time_str
                result['data']['flag'] = 'N'
                return result
            visitor_list = Sentry_Visitor().get_visitor_list(province=province,
                                                             city=city,
                                                             project=project,
                                                             page_size=int(page_size),
                                                             page_no=int(page_no),
                                                             start_time=start_time,
                                                             end_time=end_time,
                                                             coming=coming)
            if not visitor_list:
                total_count = 0
            else:
                total_count = visitor_list.count()
            result['data']['app_data_list'] = [visitor.get_visitor_info() for visitor in visitor_list]
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': total_count,
            }
        except Exception as e:
            result['msg'] = e
            result['log'] = traceback.format_exc()
            result['err'] = 1
            result['data']['flag'] = 'N'
        return result

    @jsonResponse()
    def get_visitor_list_by_project_id_list(self, outer_project_id_list=[], start_time=int(time.time()) - 30 * 24 * 3600,
                                          end_time=int(time.time())):
        '''
        @note: 根据社区ID列表获取访客预约记录数据
        @note: 访问url： /sentry_api/Sentry_Visitor_Api/get_visitor_list_by_project_id_list/1/
        @note: 测试demo:
        :param outer_project_id_list:社区ID列表
        :param start_time:开始日期
        :param end_time:结束日期
        :return:
        '''

        try:
            result = qd_result.get_default_result()

            start_time_flag, start_time_str = validate.validate_timestamp(str(start_time), "start_time")
            if not start_time_flag: return qd_result.set_err_msg(result, start_time_str)

            end_time_flag, end_time_str = validate.validate_timestamp(str(end_time), "end_day")
            if not end_time_flag: return qd_result.set_err_msg(result, end_time_str)

            if start_time and end_time and not (start_time_flag or end_time_flag):
                result['msg'] = start_time_str, end_time_str
                result['data']['flag'] = 'N'
                return result

            start_day = get_datetime_by_timestamp(timestamp=int(start_time), index=-1)
            end_day = get_datetime_by_timestamp(timestamp=int(end_time), index=1)

            outer_project_id_list = json.loads(outer_project_id_list) if isinstance(outer_project_id_list,
                                                                                    str) else outer_project_id_list

            raw_query = {
                "_brake_password.apartment.outer_project_id": {
                    "$in": outer_project_id_list
                },
                'status': '1',
                'created_time': {"$gt": start_day, "$lt": end_day}
            }

            visitor_list = Sentry_Visitor.objects(__raw__=raw_query).\
                order_by('_brake_password.apartment.outer_project_id')

            result['data']['brake_order_list'] = [visitor.get_visitor_info() for visitor in visitor_list]
            result['data']['pagination'] = {
                'total_count': visitor_list.count(),
            }
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result
