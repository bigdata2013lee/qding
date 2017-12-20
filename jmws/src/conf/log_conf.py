# coding=utf-8
import os

_LEVEL = 'DEBUG'


def _get_base_dir():
    from conf.qd_conf import CONF
    return CONF['app_home']


def _file_handler(log_fname):
    return {
        'level': 'DEBUG',
        'class': 'logging.handlers.RotatingFileHandler',
        'formatter': 'simple',
        'filename': os.path.join(_get_base_dir(), 'log/%s.log' % log_fname),
        'maxBytes': 12 * 1048576, 'backupCount': 4,
        'encoding': 'utf-8'
    }


def _log_dict(handler, level="DEBUG"):
    return {'handlers': [handler], 'level': level, 'propagate': False}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(filename)s[line:%(lineno)d] %(message)s',
        }
    },
    'handlers': {
        'null': {'level': 'DEBUG', 'class': 'logging.NullHandler'},
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'simple'}
    },
    'loggers': {
        'django.db.backends': _log_dict('null', level=_LEVEL),
    }
}


def _add(*names):
    for name in names:
        LOGGING.get("handlers")[name] = _file_handler(name)
        LOGGING.get("loggers")[name] = _log_dict(name, level=_LEVEL)


_add("django",)
_add("qdevt_bus", "qdcommevts", "sync_tasks", "intervalevts")

