# -*- coding: utf-8 -*-

import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from flask import current_app
from celery.signals import task_prerun, task_postrun

from . import db, create_celery_app
from .constants import USER_TOKEN_TAG, VERIFICATION_VALID_HOURS, CAPTCHA_VALID_MINS
from .utils import des


celery = create_celery_app()


@task_prerun.connect()
def celery_prerun(sender=None, task=None, task_id=None, *args, **kwargs):
    """
    celery任务执行前钩子函数
    :param sender:
    :param task:
    :param task_id:
    :param args:
    :param kwargs:
    :return:
    """
    if db.is_closed():
        db.connect()


@task_postrun.connect()
def celery_postrun(sender=None, task=None, task_id=None, retval=None, state=None, *args, **kwargs):
    """
    celery任务执行后钩子函数
    :param sender:
    :param task:
    :param task_id:
    :param retval:
    :param state:
    :param args:
    :param kwargs:
    :return:
    """
    if not db.is_closed():
        db.close()


@celery.task()
def send_email_verification(user):
    """
    发送验证邮件（链接）
    :param user: 
    :return: 
    """
    current_app.logger.info(u'发送验证邮件（链接）')
    smtp_server, smtp_from_addr, smtp_password = map(current_app.config['SMTP'].get, ('server', 'from_addr', 'password'))

    token = des.encrypt('%s:%s:%s' % (USER_TOKEN_TAG, user.id, int(time.time()) + 3600 * VERIFICATION_VALID_HOURS))
    url = 'http://%s/extensions/user/email_verification/?u=%s&t=%s' % (current_app.config['PROJECT_DOMAIN'], user.uuid.hex, token)
    html = u'<html><body><p><a href="%s">点击此链接进行邮箱验证</a></p><p>该链接%s小时内有效</p></body></html>' % (url, VERIFICATION_VALID_HOURS)
    message = MIMEText(html, 'html', 'utf-8')
    message['From'] = formataddr((Header(u'蔚然', 'utf-8').encode(), smtp_from_addr))
    message['To'] = formataddr((Header(user.name, 'utf-8').encode(), user.email))
    message['Subject'] = Header(u'『蔚然』邮箱验证', 'utf-8').encode()

    server = smtplib.SMTP(smtp_server)
    server.set_debuglevel(1)
    server.login(smtp_from_addr, smtp_password)
    server.sendmail(smtp_from_addr, user.email, message.as_string())
    server.quit()


@celery.task()
def send_email_captcha(captcha):
    """
    发送验证邮件（验证码）
    :param captcha: 
    :return: 
    """
    current_app.logger.info(u'发送验证邮件（验证码）')
    smtp_server, smtp_from_addr, smtp_password = map(current_app.config['SMTP'].get, ('server', 'from_addr', 'password'))

    html = u'<html><body><p>您正在进行找回密码操作，验证码为：%s（%s分钟内有效）</p></body></html>' % (captcha.code, CAPTCHA_VALID_MINS)
    message = MIMEText(html, 'html', 'utf-8')
    message['From'] = formataddr((Header(u'蔚然', 'utf-8').encode(), smtp_from_addr))
    message['To'] = formataddr((Header(captcha.user.name, 'utf-8').encode(), captcha.user.email))
    message['Subject'] = Header(u'『蔚然』找回密码', 'utf-8').encode()

    server = smtplib.SMTP(smtp_server)
    server.set_debuglevel(1)
    server.login(smtp_from_addr, smtp_password)
    server.sendmail(smtp_from_addr, captcha.user.email, message.as_string())
    server.quit()
