# -*- coding: utf-8 -*-
CONST = {
    'base': {
        'host': 'http://www.lixiaodeng.com/',
        'version': '1.6.3',
        'env': 'dev',
        'log': True,
    },
    'domain': {
        'default': 'lixiaodeng.com',
        'oss': 'lixiaodeng.com',
    },
    'email': {
        'smtp': 'smtp.qding.me',
        'sender': {
            'noreply': {
                'display_name': u'千丁互联 - 自动回复',
                'username': 'smart@qding.me',
                'password': 'Qd@2014',
            },
            'contact': {
                'display_name': '千丁互联 - 联系我们',
                'username': 'contact@qding.me',
                'password': 'qding',
            },
        },
    },
    'mysql': {
        'host': '127.0.0.1',
        'dbname': 'qdmgr_sentry_web',
        'user': 'root',
        'password': 'root',
        'port': 3306,
    },
    'mongodb': {
        'host': '127.0.0.1',
        'port': 27017,
        'db': 'qdmgr_sentry',
    },
    'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
        'password': '',
        'connect': None,
    },
    'bj_api_url': {
        'api_url': 'http://qaboss.qdingnet.com/qding-openapi/openapi/json/machine/',
        'host': 'http://devboss.qdingnet.com/',
        'api_method': {
            'sms_request': "smsRequest?body={'mobile':'%s','content':'尊敬的用户，您的验证码是：%s'}",
            'get_app_user_by_member_id': "getAppUserByMemberId?body={'memberId':'%s'}",
            'get_app_user_by_user_id': "getAppUserByUserId?body={'userId':'%s'}",
            'get_app_user_by_room_id': "getAppUserByRoomId?body={'roomId':'%s'}",
            'get_app_user_by_mobile': "getAppUserByMobile?body={'mobile':'%s'}",
            'find_project_by_name': "findProjectByName?body={'projectName':'%s'}",
            'get_room_data_by_room_id': "getRoomDataByRoomId?body={'roomId':'%s'}",
            'sys_pass_log': "syncPassLog?body={'uqineId':'%s','projectId':'%s','passType':'%s','roomId':'%s','userId':'%s','passPosition':'%s','roomName':'%s','projectName':'%s'"
        }
    },
    'sz_api_url': {
        'api_url': 'http://xqx.qdingnet.com/remote/',
        'api_method': {
            'send_password': 'bjqd.BjQdingApi.report_comm_event/'
        },
    },
    'static': {
        'url': '/static/',
        'brake_upgrade_dir': '/data/qdmgr_sentry/uploads/brake/rom/',
        'brake_upgrade_config_dir': '/data/qdmgr_sentry/uploads/brake_config/apk/',
    },
    'bj_data_url': {
        'url': 'http://devboss.qdingnet.com/sz-xml/',
        'host': 'devboss.qdingnet.com',
    },
    'debug': False,
}
