# --*-- coding:utf8 --*--
from apps.brake.api.Pass_Data_Common_Processor import Pass_Data_Common_Processor
from apps.common.utils.request_api import request_bj_server


class Pass_Data_Sync_Processor(Pass_Data_Common_Processor):
    def hand_request(self, brake_pass, result, apartment, brake_obj, sentry_visitor):
        ret = {}
        brake_machine = brake_pass.pass_info['brake_machine']
        app_user = brake_pass.pass_info.get("app_user", {})
        brake_card = brake_pass.pass_info.get("brake_card", {})

        position = brake_machine['position']
        project = position['project_list'][0]['project']
        outer_project_id = position['project_list'][0]['outer_project_id']

        ret['unique_id'] = "%s%s" % (brake_machine['mac'], int(brake_pass.created_time.timestamp()))
        room_data_list = [] if not app_user else app_user.get("room_data_list", [])
        user_type = '0' if len(room_data_list) == 0 else room_data_list[0].get('role', '0') or '0'
        ret['user_type'] = user_type
        ret['project_id'] = outer_project_id
        ret['project_name'] = project
        ret['room_id'] = room_data_list[0]['outer_room_id'] if room_data_list else ""
        ret['room_name'] = room_data_list[0]['room'] if room_data_list else ""
        ret['user_id'] = app_user.get("outer_app_user_id", "")
        ret['mobile'] = app_user.get("phone", "")
        ret['pass_time'] = int(brake_pass.created_time.timestamp())
        ret['pass_type'] = brake_machine['gate_info'].get("direction", "I")
        ret['pass_position'] = brake_machine['position_str']
        ret['pass_media'] = getattr(brake_pass, "pass_type", 0) or 0
        ret['card_no'] = brake_card.get("card_no", "")
        method_url = 'syncPassLog?body={"uqineId":"%s","projectId":"%s"' % (ret['unique_id'], ret['project_id'])
        method_url = "%s%s" % (method_url, ',"passType":"%s","roomId":"%s"' % (ret['pass_type'], ret['room_id']))
        method_url = "%s%s" % (method_url, ',"passMedia":"%s", "cardNo":"%s"' % (ret['pass_media'], ret['card_no']))
        method_url = "%s%s" % (
            method_url, ',"userId":"%s","passPosition":"%s"' % (ret['user_id'], ret['pass_position']))
        method_url = "%s%s" % (
            method_url, ',"roomName":"%s","projectName":"%s"' % (ret['room_name'], ret['project_name']))
        if brake_pass.pass_type == "2":
            ret['created_time'] = int(sentry_visitor.created_time.timestamp())
            ret['reason'] = sentry_visitor.reason
            ret['user_type'] = '1'
            method_url = "%s%s" % (
                method_url, ',"reason":"%s","createTime":"%s"' % (ret['reason'], ret['created_time']))
        method_url = "%s%s" % (method_url, ',"passTime":"%s","mobile":"%s","userType":"%s"}' % (
            ret['pass_time'], ret['mobile'], ret['user_type']))
        method_url = method_url.replace("#", "")
        request_bj_server(method_url=method_url, method_params={}, post_flag=False)
