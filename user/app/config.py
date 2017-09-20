# -*- coding: utf-8 -*-

from os import environ
from logging.handlers import RotatingFileHandler
import logging


class Config(object):
    """
    配置
    """
    _project_name = 'whalerun_user'
    PROJECT_DOMAIN = environ.get('PROJECT_DOMAIN')

    # mysql
    MYSQL = {
        'charset': 'utf8mb4',
        'host': environ.get('FLASK_MYSQL_HOST') or 'localhost',
        'port': int(environ.get('FLASK_MYSQL_PORT') or 3306),
        'user': environ.get('FLASK_MYSQL_USER') or 'root',
        'password': environ.get('FLASK_MYSQL_PASSWORD'),
        'database': environ.get('FLASK_MYSQL_DB') or _project_name
    }

    # redis
    REDIS = {
        'host': environ.get('FLASK_REDIS_HOST') or 'localhost',
        'port': int(environ.get('FLASK_REDIS_PORT') or 6379),
        'db': int(environ.get('FLASK_REDIS_DB') or 0)
    }

    # celery
    BROKER_URL = 'redis://%s:%s/%s' % (REDIS['host'], REDIS['port'], environ.get('CELERY_BROKER_DB') or 1)
    CELERY_RESULT_BACKEND = 'redis://%s:%s/%s' % (REDIS['host'], REDIS['port'], environ.get('CELERY_BACKEND_DB') or 2)
    CELERY_TASK_SERIALIZER = 'pickle'
    CELERY_ACCEPT_CONTENT = ['pickle']
    CELERY_RESULT_SERIALIZER = 'pickle'
    CELERY_TIMEZONE = 'Asia/Shanghai'

    # SMTP
    SMTP = {
        'server': environ.get('SMTP_SERVER') or 'smtpdm.aliyun.com',
        'from_addr': environ.get('SMTP_FROM_ADDR'),
        'password': environ.get('SMTP_PASSWORD')
    }

    @classmethod
    def init_app(cls, app):
        """
        初始化flask应用对象
        :param app:
        :return:
        """
        file_handler = RotatingFileHandler(environ.get('FLASK_LOGFILE') or '%s.log' % cls._project_name,
                                           maxBytes=1024 * 1024 * 100, backupCount=10, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter(u'[%(asctime)s] - %(pathname)s (%(lineno)s) - [%(levelname)s] - %(message)s'))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
