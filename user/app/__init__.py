# -*- coding: utf-8 -*-

from flask import Flask
from peewee import MySQLDatabase
from redis import StrictRedis
from celery import Celery

from .config import Config


db = MySQLDatabase(None)
redis_client = StrictRedis(**Config.REDIS)

app_instance = None


def create_app():
    """
    创建flask应用对象
    :return:
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)
    db.init(**app.config['MYSQL'])

    from .models import models
    db.create_tables(models, safe=True)

    from .hooks import before_app_request, after_app_request
    app.before_request(before_app_request)
    app.teardown_request(after_app_request)

    from .blueprints.api import bp_api
    app.register_blueprint(bp_api, url_prefix='/api')
    return app


def create_celery_app(app=None):
    """
    创建celery应用对象
    :param app:
    :return:
    """
    app = app or create_app()
    celery = Celery(app.import_name)
    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery

