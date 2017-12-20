# coding=utf-8


# 用于扩展或重写部分默认配置
ENV_CONF = {
    'wifi_ota_server': ('10.39.249.186', 9556),

    'redis': {
        #'pattern': "sentinel",
        'pattern': "single",

        'comm_confs': {},
        'sentinel': {'servers': [('10.9.86.231', 26379), ('10.9.198.240', 26379)], 'master_alias': 'mymaster'},
        'single': {'host': 'store', 'port': 6379},
    },
    'mongo': {'db': 'cloud_talk', 'host': 'store', 'port': 27017},

}


DOMAIN_CONF = {
    'domains': ['www.qdingnet.com', 'sz.qdingnet.com'],

    'www.qdingnet.com': {

        "apis": {
            "push_api": "http://qa-api.qdingnet.com/qding-openapi/openapi/json/machine/pushRequest",
            "get_user_info": "http://qa-api.qdingnet.com/qding-openapi/openapi/json/machine/getAppUserByMemberId",
            "check_role": "http://qa-api.qdingnet.com/qding-openapi/openapi/json/machine/checkRole",
            "xml_download_url": "http://qa-api.qdingnet.com/sz-xml"
        }

    }
}