# -*- coding: utf-8 -*-

from apps.web.classes.Web_User import Web_User
import hashlib

Web_User(user_type=11, username='qding', password=hashlib.md5('qding123'.encode()).hexdigest()).add_user()
Web_User(user_type=20, username='千丁管理员', password=hashlib.md5('sentry123'.encode()).hexdigest()).add_user()
Web_User(user_type=21, username='card', password=hashlib.md5('card123'.encode()).hexdigest()).add_user()
Web_User(user_type=40, brake_config_password=hashlib.md5('123456'.encode()).hexdigest(), phone="12345678901").add_user()
