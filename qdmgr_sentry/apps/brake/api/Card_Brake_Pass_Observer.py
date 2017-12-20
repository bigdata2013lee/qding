# -*- coding:utf8 -*-
from apps.brake.api.Observer import Observer


class Card_Brake_Pass_Observer(Observer):
    def __init__(self, brake_pass_subject=None):
        self.brake_pass_subject = brake_pass_subject
        self.brake_pass_subject.set_observer(self)

    def insert_pass(self, brake_machine, pass_media, brake_pass):
        brake_pass.user_type = '0'

        brake_pass.pass_info = {
            "brake_machine": brake_machine,
            "brake_card": pass_media,
        }
        return True, ""
