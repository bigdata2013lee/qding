# coding=utf-8


# 用于扩展或重写部分默认配置
ENV_CONF = {

    'redis': {
        #'pattern': "sentinel",
        'pattern': "single",

        'comm_confs': {},
        #'sentinel': {'servers': [('10.9.86.231', 26379), ('10.9.198.240', 26379)], 'master_alias': 'mymaster'},
        'single': {'host': '10.39.249.186', 'port': 6371},
    },
    'mongo': {'db': 'jmws', 'host': '10.39.249.186', 'port': 27017},
}

