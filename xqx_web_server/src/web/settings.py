# -*- coding: utf-8 -*-
import os

from conf import log_conf
from conf import qd_conf

APPEND_SLASH = True
DEBUG = True

ROOT_URLCONF = 'web.urls.urls'
WSGI_APPLICATION = 'wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django_extensions',
    'web',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(qd_conf.CONF['app_home'], 'var/app.db'),
    }

}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qdtalk_8td@h11eu_zn1+__n=ukqb415632tzn0n=c6_dhr23%=!^1s1pzsc5bp'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True
SESSION_COOKIE_AGE = 3600 * 1  # 1小时

SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_PREFIX = 'websession'
SESSION_REDIS_SOCKET_TIMEOUT = 1
SESSION_REDIS_DB = 2


# Redis Single
if qd_conf.CONF.get("redis").get("pattern") == "single":
    SESSION_REDIS_HOST = qd_conf.CONF.get("redis").get("single").get("host")
    SESSION_REDIS_PORT = qd_conf.CONF.get("redis").get("single").get("port")


# Redis Sentinel
elif qd_conf.CONF.get("redis").get("pattern") == "sentinel":
    SESSION_REDIS_SENTINEL_LIST = qd_conf.CONF.get("redis").get("sentinel").get("servers")
    SESSION_REDIS_SENTINEL_MASTER_ALIAS = qd_conf.CONF.get("redis").get("sentinel").get("master_alias")


# Templates definition
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(qd_conf.CONF['app_home'], "src/web/templates")],
    },

]

LOGGING = log_conf.LOGGING
