# -*- coding: utf-8 -*-

from .const import CONST

import os
import sys
import datetime
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.insert(0, BASE_DIR)

DEBUG = True
TEMPLATE_DEBUG = DEBUG


SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3 * 3600  # 90 days


from mongoengine import connect
connect("qdmgr_sentry", host="mongodb://%s/%s" % (CONST['mongodb']['host'], CONST['mongodb']['db']),
        port=CONST['mongodb']['port'], connect=False)



ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': CONST['mysql']['dbname'],  # Or path to database file if using sqlite3.
        'USER': CONST['mysql']['user'],  # Not used with sqlite3.
        'PASSWORD': CONST['mysql']['password'],  # Not used with sqlite3.
        'HOST': CONST['mysql']['host'],  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': CONST['mysql']['port'],  # Set to empty string for default. Not used with sqlite3.
        'CHARSET': 'utf8',
        'TIMEOUT': 15,
    },
}


TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
SECRET_KEY = '7$k7^=q90h1=!np@e%p6@qrafau2paq_zzx(y!5)wq76v&amp;_)t&amp;'

USE_I18N = True
USE_L10N = True
USE_TZ = False

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = CONST['static']['url']

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'apps/community/static'),
    os.path.join(BASE_DIR, 'apps/common/static'),
    os.path.join(BASE_DIR, 'apps/manage/static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


TEMPLATE_LOADERS = (
    'django_jinja.loaders.FileSystemLoader',
    'django_jinja.loaders.AppLoader',
)

DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.html'
JINJA2_AUTOESCAPE = True
JINJA2_MUTE_URLRESOLVE_EXCEPTIONS = True
JINJA2_FILTERS_REPLACE_FROM_DJANGO = False
JINJA2_BYTECODE_CACHE_ENABLE = False

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

MIDDLEWARE_CLASSES = (
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'apps.common.utils.middleware.SetRemoteAddrFromForwardedFor',
    'apps.common.utils.middleware.ExceptionMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
)

ROOT_URLCONF = 'apps.common.urls.direct'
ROOT_HOSTCONF = 'settings.hosts'
DEFAULT_HOST = 'sentry'

WSGI_APPLICATION = 'settings.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'apps/community/templates'),
    os.path.join(BASE_DIR, 'apps/common/templates'),
    os.path.join(BASE_DIR, 'apps/common/templates/common'),
    os.path.join(BASE_DIR, 'apps/manage/templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'apps.common.utils.context_processor.AddConstContext',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_extensions',
    'django_hosts',
    'django_jinja',
    'apps.common',
    'apps.manage',
    'apps.community',
    'apps.basedata',
    'apps.async',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s',
        }
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': os.path.join(BASE_DIR, 'logs/debug-%s.log' % datetime.datetime.now().strftime('%Y%m%d')),
            'encoding': 'utf8',
        },
    },
    'loggers': {
        'qding': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
