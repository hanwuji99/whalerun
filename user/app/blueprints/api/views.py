# -*- coding: utf-8 -*-
import time
import datetime
import random

from flask import request, g

from ...models import User, Captcha
from ...api_utils import *
from ...constants import MIN_PASSWORD_LEN, MAX_PASSWORD_LEN, USER_TOKEN_TAG, USER_LOGIN_VALID_DAYS, CAPTCHA_CODE_LEN, \
    CAPTCHA_VALID_MINS, DEFAULT_AVATARS
from ...utils import des
from ...utils.key_util import generate_random_key
from ...utils.pattern_util import check_email

from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
# from . import bp_api
class App():
    app = None

    def set_app(app):
        App.app = app

    @classmethod
    def get_app(cls):
        return App.app

# global github_oauth
# oauth = github_oauth.get_oauth()
# global makeapp
# app = makeapp.get_app()

app = App.get_app()
# app.debug = True
# app.secret_key = 'development'
oauth = OAuth(app)
#
github = oauth.remote_app(
    'github',
    consumer_key='1ec3398f773522ea93a2',
    consumer_secret='356740a0ba53c57de3ef794850bedcf61bd84ef3',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)
#

@app.route('/index')
def index():
    if 'github_token' in session:
        me = github.get('user')
        return jsonify(me.data)
    return redirect(url_for('github_login'))


@app.route('/users/github_login')
def github_login():
    return github.authorize(callback=url_for('github_authorized', _external=True))


@app.route('/users/github_login/authorized')
def github_authorized():
    resp = github.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['github_token'] = (resp['access_token'], '')
    me = github.get('user')
    return jsonify(me.data)


@app.route('/users/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')
#

# @bp_api.route('/current_user/', methods=['GET'])
# def get_current_user():
#     """
#     获取当前用户详情
#     :return:
#     """
#     token = request.args.get('token')
#     claim_args(1201, token)
#     user = User.query_by_token(token)
#     claim_args_true(1104, user)
#
#     data = {
#         'user': user.to_dict(g.fields)
#     }
#     return api_success_response(data)

#
# @bp_api.route('/users/', methods=['GET'])
# def list_users():
#     """
#     列出用户
#     :return:
#     """
#     ids, uuids, order_by, page, per_page, email, email_verified, blocked, featured = map(
#         request.args.get,
#         ('ids', 'uuids', 'order_by', 'page', 'per_page', 'email', 'email_verified', 'blocked', 'featured')
#     )
#     ids = ids.split(',') if ids else None
#     uuids = uuids.split(',') if uuids else None
#     order_by = order_by.split(',') if order_by else None
#     claim_args_digits_string(1202, *filter(None, (page, per_page)))
#     for _arg in [email_verified, blocked, featured]:
#         if _arg:
#             claim_args_true(1202, _arg in ['0', '1'])
#
#     select_query = User.select()
#     if ids:
#         select_query = select_query.where(User.id << ids)
#     if uuids:
#         select_query = select_query.where(User.uuid << uuids)
#     if email_verified:
#         select_query = select_query.where(User.email_verified == bool(int(email_verified)))
#     if blocked:
#         select_query = select_query.where(User.blocked == bool(int(blocked)))
#     if featured:
#         select_query = select_query.where(User.featured == bool(int(featured)))
#     if email:
#         select_query = select_query.where(User.email == email)
#     data = {
#         'users': [obj.to_dict(g.fields) for obj in User.iterator(select_query, order_by, page, per_page)],
#         'total': User.count(select_query)
#     }
#     return api_success_response(data)

#
# @bp_api.route('/users/', methods=['POST'])
# def create_user():
#     """
#     创建用户
#     :return:
#     """
#     email, password, name = map(g.json.get, ('email', 'password', 'name'))
#     claim_args(1401, email, password, name)
#     claim_args_string(1402, email, password, name)
#     claim_args_true(1410, check_email(email))
#     claim_args_true(1412, not User.query_by_email(email))
#     claim_args_true(1414, MIN_PASSWORD_LEN <= len(password) <= MAX_PASSWORD_LEN)
#
#     user = User.create_user(email, password, name, random.choice(DEFAULT_AVATARS))
#     token = des.encrypt('%s:%s:%s' % (USER_TOKEN_TAG, user.id, int(time.time()) + 86400 * USER_LOGIN_VALID_DAYS))
#     data = {
#         'user': user.to_dict(g.fields),
#         'token': token
#     }
#     user.login()
#
#     from ...tasks import send_email_verification
#     send_email_verification.delay(user)  # celery task
#     return api_success_response(data)

#
# @bp_api.route('/users/login/', methods=['PUT'])
# def user_login():
#     """
#     用户登录
#     :return:
#     """
#     email, password = map(g.json.get, ('email', 'password'))
#     claim_args(1401, email, password)
#     claim_args_string(1402, email, password)
#     user = User.query_by_email(email)
#     claim_args_true(1411, user)
#     claim_args_true(1413, user.check_password(password))
#     claim_args_true(1103, not user.blocked)
#
#     token = des.encrypt('%s:%s:%s' % (USER_TOKEN_TAG, user.id, int(time.time()) + 86400 * USER_LOGIN_VALID_DAYS))
#     data = {
#         'user': user.to_dict(g.fields),
#         'token': token
#     }
#     user.login()
#     return api_success_response(data)

#
# @bp_api.route('/users/verification_email/', methods=['POST'])
# def send_verification_email():
#     """
#     发送验证邮件（链接）
#     :return:
#     """
#     user_id, email = map(g.json.get, ('user_id', 'email'))
#     claim_args_true(1401, any([user_id, email]))
#     user = User.query_by_id_or_email(user_id, email)
#     claim_args_true(1411, user)
#     claim_args_true(1417, not user.email_verified)
#
#     from ...tasks import send_email_verification
#     send_email_verification.delay(user)  # celery task
#     return api_success_response({})

#
# @bp_api.route('/users/email_verified/', methods=['PUT'])
# def validate_user_email():
#     """
#     用户邮箱通过验证
#     :return:
#     """
#     user_uuid, token = map(g.json.get, ('user_uuid', 'token'))
#     claim_args(1401, user_uuid, token)
#     claim_args_string(1402, user_uuid, token)
#     user = User.query_by_token(token)
#     claim_args_true(1411, user and user == User.query_by_uuid(user_uuid))
#
#     user.email_verified = True
#     user.update_time = datetime.datetime.now()
#     user.save()
#     data = {
#         'user': user.to_dict(g.fields)
#     }
#     return api_success_response(data)

#
# @bp_api.route('/users/password/', methods=['PUT'])
# def update_user_password():
#     """
#     修改用户密码
#     :return:
#     """
#     user_id, email, code, password_old, password_new = map(g.json.get,
#                                                            ('user_id', 'email', 'code', 'password_old', 'password_new'))
#     claim_args_true(1401, any([user_id, email]), any([code, password_old]))
#     claim_args(1401, password_new)
#     claim_args_string(1402, password_new)
#     claim_args_true(1414, MIN_PASSWORD_LEN <= len(password_new) <= MAX_PASSWORD_LEN)
#     user = User.query_by_id_or_email(user_id, email)
#     claim_args_true(1411, user)
#     if code:
#         claim_args_string(1402, code)
#         captcha = Captcha.query_latest_captcha(user, 1)
#         claim_args_true(1415, captcha and captcha.code == code)
#         claim_args_true(1416,
#                         captcha.create_time + datetime.timedelta(minutes=CAPTCHA_VALID_MINS) > datetime.datetime.now())
#     elif password_old:
#         claim_args_string(1402, password_old)
#         claim_args_true(1413, user.check_password(password_old))
#
#     user = user.change_password(password_new)
#     data = {
#         'user': user.to_dict(g.fields)
#     }
#     return api_success_response(data)

#
# @bp_api.route('/users/name/', methods=['PUT'])
# def update_user_name():
#     """
#     修改用户昵称
#     :return:
#     """
#     user_id, email, name = map(g.json.get, ('user_id', 'email', 'name'))
#     claim_args_true(1401, any([user_id, email]))
#     claim_args(1401, name)
#     claim_args_string(1402, name)
#     user = User.query_by_id_or_email(user_id, email)
#     claim_args_true(1411, user)
#
#     user.name = name.strip()
#     user.update_time = datetime.datetime.now()
#     user.save()
#     data = {
#         'user': user.to_dict(g.fields)
#     }
#     return api_success_response(data)
#
#
# @bp_api.route('/users/avatar/', methods=['PUT'])
# def update_user_avatar():
#     """
#     修改用户头像
#     :return:
#     """
#     user_id, email, avatar = map(g.json.get, ('user_id', 'email', 'avatar'))
#     claim_args_true(1401, any([user_id, email]))
#     if avatar:
#         claim_args_string(1402, avatar)
#     user = User.query_by_id_or_email(user_id, email)
#     claim_args_true(1411, user)
#
#     user.avatar = avatar or None
#     user.update_time = datetime.datetime.now()
#     user.save()
#     data = {
#         'user': user.to_dict(g.fields)
#     }
#     return api_success_response(data)
#
#
# @bp_api.route('/captcha/', methods=['POST'])
# def create_captcha():
#     """
#     创建验证码
#     :return:
#     """
#     user_id, email, group = map(g.json.get, ('user_id', 'email', 'group'))
#     claim_args_true(1401, any([user_id, email]))
#     claim_args(1401, group)
#     claim_args_true(1402, group in [1])
#     user = User.query_by_id_or_email(user_id, email)
#     claim_args_true(1411, user)
#
#     code = generate_random_key(CAPTCHA_CODE_LEN)
#     captcha = Captcha.create_captcha(user, group, code)
#     data = {
#         'captcha': captcha.to_dict(g.fields)
#     }
#
#     from ...tasks import send_email_captcha
#     send_email_captcha.delay(captcha)  # celery task
#     return api_success_response(data)
#
#
# @bp_api.route('/captcha/check/', methods=['PUT'])
# def check_captcha():
#     """
#     核对验证码
#     :return:
#     """
#     user_id, email, group, code = map(g.json.get, ('user_id', 'email', 'group', 'code'))
#     claim_args_true(1401, any([user_id, email]))
#     claim_args(1401, group, code)
#     claim_args_true(1402, group in [1])
#     claim_args_string(1402, code)
#     user = User.query_by_id_or_email(user_id, email)
#     claim_args_true(1411, user)
#     captcha = Captcha.query_latest_captcha(user, group)
#     claim_args_true(1415, captcha and captcha.code == code)
#     claim_args_true(1416,
#                     captcha.create_time + datetime.timedelta(minutes=CAPTCHA_VALID_MINS) > datetime.datetime.now())
#     return api_success_response({})
