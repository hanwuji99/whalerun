# -*- coding: utf-8 -*-

import time
import datetime
from uuid import uuid1

from flask import current_app
from peewee import *
from playhouse.shortcuts import model_to_dict
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .constants import DEFAULT_PER_PAGE, USER_TOKEN_TAG
from .utils import des


_to_set = (lambda r: set(r) if r else set())
_nullable_strip = (lambda s: s.strip() or None if s else None)


class BaseModel(Model):
    """
    所有model的基类
    """
    id = PrimaryKeyField()  # 主键
    uuid = UUIDField(unique=True, default=uuid1)  # UUID
    create_time = DateTimeField(default=datetime.datetime.now)  # 创建时间
    update_time = DateTimeField(default=datetime.datetime.now)  # 更新时间
    weight = IntegerField(default=0)  # 排序权重

    class Meta:
        database = db
        only_save_dirty = True

    @classmethod
    def _exclude_fields(cls):
        """
        转换为dict表示时排除在外的字段
        :return:
        """
        return {'create_time', 'update_time'}

    @classmethod
    def _extra_attributes(cls):
        """
        转换为dict表示时额外增加的属性
        :return:
        """
        return {'iso_create_time', 'iso_update_time'}

    @classmethod
    def query_by_id(cls, _id):
        """
        根据id查询
        :param _id:
        :return:
        """
        obj = None
        try:
            obj = cls.get(cls.id == _id)
        finally:
            return obj

    @classmethod
    def query_by_uuid(cls, _uuid):
        """
        根据uuid查询
        :param _uuid:
        :return:
        """
        obj = None
        try:
            obj = cls.get(cls.uuid == _uuid)
        finally:
            return obj

    @classmethod
    def count(cls, select_query=None):
        """
        根据查询条件计数
        :param select_query: [SelectQuery or None]
        :return:
        """
        cnt = 0
        try:
            if select_query is None:
                select_query = cls.select()
            cnt = select_query.count()
        finally:
            return cnt

    @classmethod
    def iterator(cls, select_query=None, order_by=None, page=None, per_page=None):
        """
        根据查询条件返回迭代器
        :param select_query: [SelectQuery or None]
        :param order_by: [iterable or None]
        :param page:
        :param per_page:
        :return:
        """
        try:
            if select_query is None:
                select_query = cls.select()

            if order_by:
                _fields = cls._meta.fields
                clauses = []
                for item in order_by:
                    desc, attr = item.startswith('-'), item.lstrip('+-')
                    if attr in cls._exclude_fields():
                        continue
                    if attr in cls._extra_attributes():
                        attr = attr.split('_', 1)[-1]
                    if attr in _fields:
                        clauses.append(_fields[attr].desc() if desc else _fields[attr])
                if clauses:
                    select_query = select_query.order_by(*clauses)

            if page or per_page:
                select_query = select_query.paginate(int(page or 1), int(per_page or DEFAULT_PER_PAGE))

            return select_query.naive().iterator()

        except Exception, e:
            current_app.logger.error(e)
            return iter([])

    def to_dict(self, only=None, exclude=None, recurse=False, backrefs=False, max_depth=None):
        """
        转换为dict表示
        :param only: [iterable or None]
        :param exclude: [iterable or None]
        :param recurse: [bool]
        :param backrefs: [bool]
        :param max_depth:
        :return:
        """
        try:
            only = _to_set(only)
            exclude = _to_set(exclude) | self._exclude_fields()

            _fields = self._meta.fields
            only_fields = {_fields[k] for k in only if k in _fields}
            exclude_fields = {_fields[k] for k in exclude if k in _fields}
            extra_attrs = self._extra_attributes() - exclude
            if only:
                extra_attrs &= only
                if not only_fields:
                    exclude_fields = _fields.values()

            return model_to_dict(self, recurse=recurse, backrefs=backrefs, only=only_fields, exclude=exclude_fields,
                                 extra_attrs=extra_attrs, max_depth=max_depth)

        except Exception, e:
            current_app.logger.error(e)
            return {}

    def modified_fields(self, exclude=None):
        """
        与数据库中对应的数据相比，数值有变动的字段名称列表
        :param exclude: [iterable or None]
        :return:
        """
        try:
            exclude = _to_set(exclude)
            db_obj = self.query_by_id(self.id)
            return filter(lambda f: getattr(self, f) != getattr(db_obj, f) and f not in exclude,
                          self._meta.sorted_field_names)

        except Exception, e:
            current_app.logger.error(e)

    def change_weight(self, weight):
        """
        修改排序权重
        :param weight:
        :return:
        """
        try:
            self.weight = weight
            self.save()
            return self

        except Exception, e:
            current_app.logger.error(e)

    def iso_create_time(self):
        return self.create_time.isoformat()

    def iso_update_time(self):
        return self.update_time.isoformat()


class User(BaseModel):
    """
    用户
    """
    email = CharField(max_length=80, null=True, index=True)  # 邮箱
    password = CharField(default='')  # 密码
    name = CharField(null=True)  # 昵称
    avatar = CharField(null=True)  # 头像图片url

    last_login = DateTimeField(null=True)  # 最近登录时间
    last_active = DateTimeField(null=True)  # 最近活跃时间

    email_verified = BooleanField(default=False)  # 是否已验证邮箱
    blocked = BooleanField(default=False)  # 是否禁止登录
    featured = BooleanField(default=False)  # 是否推荐

    class Meta:
        db_table = 'user'

    @classmethod
    def _exclude_fields(cls):
        return BaseModel._exclude_fields() | {'password', 'last_login', 'last_active'}

    @classmethod
    def _extra_attributes(cls):
        return BaseModel._extra_attributes() | {'iso_last_login', 'iso_last_active'}

    @classmethod
    def query_by_email(cls, email):
        """
        根据邮箱查询
        :param email:
        :return:
        """
        obj = None
        try:
            obj = cls.get(cls.email == email)
        finally:
            return obj

    @classmethod
    def query_by_id_or_email(cls, _id=None, email=None):
        """
        根据id或邮箱查询
        :param _id: 
        :param email: 
        :return: 
        """
        obj = None
        try:
            if _id:
                obj = cls.query_by_id(_id)
            elif email:
                obj = cls.query_by_email(email)
        finally:
            return obj

    @classmethod
    def query_by_token(cls, token):
        """
        根据token查询
        :param token: 
        :return: 
        """
        obj = None
        try:
            tag, _id, expires = des.decrypt(token).split(':')
            assert tag == USER_TOKEN_TAG, 'Token tag error: %s' % tag
            assert int(expires) > time.time(), 'Token expires'
            obj = cls.query_by_id(_id)
        except Exception, e:
            current_app.logger.error(e)
        finally:
            return obj

    @classmethod
    def create_user(cls, email=None, password='', name=None, avatar=None):
        """
        创建用户
        :param email:
        :param password:
        :param name:
        :param avatar:
        :return:
        """
        try:
            return cls.create(
                email=_nullable_strip(email),
                password=generate_password_hash(password) if password else '',
                name=_nullable_strip(name),
                avatar=_nullable_strip(avatar)
            )

        except Exception, e:
            current_app.logger.error(e)

    def check_password(self, password):
        """
        核对密码
        :param password:
        :return:
        """
        return check_password_hash(self.password, password)

    def change_password(self, password):
        """
        修改密码
        :param password:
        :return:
        """
        try:
            self.password = generate_password_hash(password)
            self.update_time = datetime.datetime.now()
            self.save()
            return self

        except Exception, e:
            current_app.logger.error(e)

    def login(self):
        """
        登录
        :return:
        """
        try:
            self.last_login = datetime.datetime.now()
            self.last_active = datetime.datetime.now()
            self.save()
            return self

        except Exception, e:
            current_app.logger.error(e)

    def active(self):
        """
        活跃
        :return:
        """
        try:
            self.last_active = datetime.datetime.now()
            self.save()
            return self

        except Exception, e:
            current_app.logger.error(e)

    def iso_last_login(self):
        return self.last_login.isoformat() if self.last_login else None

    def iso_last_active(self):
        return self.last_active.isoformat() if self.last_active else None


class Captcha(BaseModel):
    """
    验证码
    """
    GROUP_CHOICES = (
        (1, u'找回密码验证码'),
    )
    user = ForeignKeyField(User, on_delete='CASCADE')
    group = IntegerField(choices=GROUP_CHOICES)  # 分组
    code = CharField()  # 验证码

    class Meta:
        db_table = 'captcha'

    @classmethod
    def query_latest_captcha(cls, user, group):
        """
        根据用户和分组查询最近的验证码
        :param user: 
        :param group: 
        :return: 
        """
        captcha = None
        try:
            captcha = cls.select().where(cls.user == user, cls.group == group).order_by(cls.id.desc()).get()
        finally:
            return captcha

    @classmethod
    def create_captcha(cls, user, group, code):
        """
        创建验证码
        :param user: 
        :param group: 
        :param code: 
        :return: 
        """
        try:
            return cls.create(
                user=user,
                group=group,
                code=code
            )

        except Exception, e:
            current_app.logger.error(e)


models = [User, Captcha]
