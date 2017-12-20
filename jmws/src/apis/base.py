# -*- coding: utf-8 -*-
import logging
import threading

log = logging.getLogger('django')

api_thread_local = threading.local()


class RequestDict(dict):
    def __init__(self):
        super(RequestDict, self).__init__()
        self.session = {}
        self.FILES = {}


class BaseApi(object):
    def __init__(self):
        self._request = None

    @property
    def request(self):
        if self._request is not None:
            return self._request

        return getattr(api_thread_local, "request", None)

    def _set_request(self, req):
        self._request = req
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
        raise Exception("Can not get login user")

    def _get_login_device(self):
        raise Exception("Can not found device object.")
