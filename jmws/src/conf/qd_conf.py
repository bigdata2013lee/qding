# coding=utf-8

import os

from conf.env_conf import ENV_CONF

CONF = {

    'app_home': os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")),
    'mail_from': dict(smtp_server="smtp.qding.me", user="smart@qding.me", password="Qd@2014"),
    'mail_sys_users': ["chenqizheng@qding.me"],

}

CONF.update(ENV_CONF)


