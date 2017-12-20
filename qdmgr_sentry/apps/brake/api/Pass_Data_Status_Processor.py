# -*- coding:utf8 -*-
from apps.brake.api.Pass_Data_Common_Processor import Pass_Data_Common_Processor
from apps.common.utils.sentry_date import get_str_day_by_datetime
from apps.common.utils.redis_client import rc
import pickle, datetime, logging

logger = logging.getLogger('qding')


class Pass_Data_Status_Processor(Pass_Data_Common_Processor):
    def hand_request(self, brake_pass, result, apartment, brake_obj, sentry_visitor):
        '''
        update brake machine newest pass time
        '''
        pass_time = int(brake_obj.updated_time.timestamp())
        created_time = int(brake_pass.created_time.timestamp())
        if pass_time < created_time: pass_time = created_time
        brake_obj.updated_time = datetime.datetime.fromtimestamp(pass_time)
        brake_obj.save()

        day = get_str_day_by_datetime(brake_pass.created_time)
        position = brake_pass.pass_info['brake_machine']['position']
        province = position['province']
        city = position['city']
        project = position['project_list'][0]['project']
        keys = "%s#%s#%s#%s" % (day, province, city, project)
        redis_ret = rc.get(keys)
        if redis_ret:
            ret = pickle.loads(redis_ret)
            level = brake_obj.position.get("level", 0) or 0
            if level in [2, 3]:
                ret['cummunity_gate_pass_num'] += 1
            elif level in [4, 5]:
                ret['unit_gate_pass_num'] += 1
        else:
            ret = brake_pass.set_project_day_pass_count(province, city, project, day)
        rc.set(keys, pickle.dumps(ret))
        if self.processor is not None:
            self.processor.hand_request(brake_pass, result, apartment, brake_obj, sentry_visitor)
