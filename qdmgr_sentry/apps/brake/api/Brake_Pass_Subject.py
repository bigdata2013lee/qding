# -*- coding:utf8 -*-
from apps.brake.api.Subject import Subject


class Brake_Pass_Subject(Subject):
    def __init__(self):
        self.observer = None

    def set_observer(self, observer):
        self.observer = observer

    def notify_observer(self):
        return self.observer.insert_pass(self.brake_machine, self.pass_media, self.brake_pass)

    def set_pass_data(self, brake_machine, pass_media, brake_pass):
        self.brake_machine = brake_machine
        self.pass_media = pass_media
        self.brake_pass = brake_pass
        return self.notify_observer()
