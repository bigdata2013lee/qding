# -*- coding: utf-8 -*-
from models.device import AioManager


class RequestDict(dict):
    def __init__(self):
        super(RequestDict, self).__init__()
        self.session = {}
        self.FILES = {}


class BaseApi(object):
    def __init__(self):
        self.request = RequestDict()

    def _set_request(self, req):
        self.request = req
        return self

    def _get_http_scheme_host(self):
        scheme = self.request.scheme
        http_host = self.request.get_host()

        return "%s://%s" % (scheme, http_host)

    def _vlogin_app_user(self, user_id):
        session_item = {'app_user_id': user_id}
        self.request.session.update(session_item)

    def _vlogin_supervisor(self, user_id):
        session_item = {
            "mgr_user_id": user_id
        }
        self.request.session.update(session_item)

    def _vlogout(self):
        self.request.session.clear()  # 清除session


    def _set_logined(self, login_type, login_id):

        self.request.session.flush()
        self.request.session['is_logined'] = True
        self.request.session['user_type'] = login_type
        self.request.session['%s_id' % login_type] = "%s" % login_id


    def _get_login_user(self):
        from models.account import QdUser
        from models.account import MgrUser
        from models.account import WuyeUser
        from models.device import Gate

        user_type = self.request.session.get("user_type", "")
        user_id = self.request.session.get(user_type + "_id", "")
        if user_type == "app_user":
            return QdUser.objects(id=user_id).first()

        elif user_type == "wuye_user":
            return WuyeUser.objects(id=user_id).first()

        elif user_type == "mgr_user":
            return MgrUser.objects(id=user_id).first()

        elif user_type == "gate":
            return Gate.objects(id=user_id).first()

        elif user_type == 'aio':
            return AioManager.objects(id=user_id).first()

        else:
            raise Exception("Can not get login user, user_type:%s, user_id:%s" % (user_type, user_id))


    def _get_login_device(self):


        from models.device import Gate

        user_type = self.request.session.get("user_type", "")
        user_id = self.request.session.get(user_type + "_id", "")

        dev = None
        if user_type == "gate":
            dev = Gate.objects(id=user_id).first()

        elif user_type == "aio":
            dev = AioManager.objects(id=user_id).first()

        else:
            raise Exception("Can not get login device, user_type:%s, user_id:%s" % (user_type, user_id))

        if not dev:
            raise Exception("Can not found device object.")

        return dev
