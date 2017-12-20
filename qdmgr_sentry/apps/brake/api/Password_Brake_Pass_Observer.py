# -*- coding:utf8 -*-
from apps.brake.api.Observer import Observer


class Password_Brake_Pass_Observer(Observer):
    def __init__(self, brake_pass_subject=None, sentry_visitor=None):
        self.brake_pass_subject = brake_pass_subject
        self.sentry_visitor = sentry_visitor
        self.brake_pass_subject.set_observer(self)

    def insert_pass(self, brake_machine, pass_media, brake_pass):
        brake_pass.user_type = '1'
        bj_app_user = getattr(pass_media, "bj_app_user", None) or None
        if not bj_app_user:
            return False, "Password_Brake_Pass_Observer: not get app user"
        if pass_media.valid_num > 0:
            pass_media.valid_num -= 1
            pass_media.save()

        self.sentry_visitor.coming = "1"
        self.sentry_visitor.save()

        brake_pass.pass_info = {
            "brake_machine": brake_machine,
            "app_user": bj_app_user.get_app_info_for_pass(),
            "brake_password": {
                "password": pass_media.password,
                "apartment": pass_media.apartment_dict,
            }
        }
        return True, ""
