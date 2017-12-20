# coding=utf-8

import os

from conf.env_conf import ENV_CONF, DOMAIN_CONF

CONF = {
    'agwsocket_port': 9555,
    'websocket_port': 9557,

    'agw_heartbeat': {"wifi_ex": 30 * 3, "gsm_ex": 300 * 3},
    'app_home': os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")),
    'jpush': {
        'app_key': '8afe57edfb58418ca8bb851b',
        'master_secret': '1ab2a3840f3de8ca93f17c4d'
    },
    'no_project_control_strategy_app': ['little_elephant'],
    'component_type_list': ['little_elephant', 'wuye_manager', 'gate'],
    'gridfs': 'gridfs',
    'mail_from': dict(smtp_server="smtp.qding.me", user="smart@qding.me", password="Qd@2014"),
    'mail_sys_users': ["chenqizheng@qding.me"],
    'xml_dir': 'var' + os.sep + 'xml' + os.sep

}

CONF.update(ENV_CONF)
CONF.update({"domain": DOMAIN_CONF})


