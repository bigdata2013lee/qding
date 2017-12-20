# -*- coding: utf-8 -*-
import os
from django.conf import settings

CONST = {
    'test_app_user_id': 'qd123',
    'xml_dir': settings.BASE_DIR + os.sep + "uploads" + os.sep + "xml" + os.sep,
    'libmeshsubV2_dir': settings.BASE_DIR + os.sep + 'uploads' + os.sep + 'brake' + os.sep + 'libmeshsubV2.so',
    'libmeshsubV3_dir': settings.BASE_DIR + os.sep + 'uploads' + os.sep + 'brake' + os.sep + 'libmeshsubV3.so',
    'brake_relative_dir': 'uploads' + os.sep + 'brake' + os.sep + 'rom' + os.sep,
    'brake_config_relative_dir': 'uploads' + os.sep + 'brake_config' + os.sep + 'apk' + os.sep,
    #'base_data_sync_email_list': ['zhouying@qding.me', 'wanghonglei@qding.me', 'lixiaodeng@qding.me', 'wangluanyu@qding.me', 'yinlaifeng@qding.me'],
    'base_data_sync_email_list': ['lixiaodeng@qding.me', '894665962@qq.com'],
}
