# -*- coding: utf-8 -*-

from flask import Blueprint

from ...api_utils import *


bp_api = Blueprint('bp_api', __name__)

bp_api.register_error_handler(APIException, handle_api_exception)
bp_api.register_error_handler(400, handle_400_error)
bp_api.register_error_handler(401, handle_401_error)
bp_api.register_error_handler(403, handle_403_error)
bp_api.register_error_handler(404, handle_404_error)
bp_api.register_error_handler(500, handle_500_error)
bp_api.before_request(before_api_request)
from . import views

from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth



class Oauth(object):
    def __init__(self,app):
        self.oauth = OAuth(app)

    def set_oauth(self, app):
        self.oauth = OAuth(app)

    def get_oauth(self):
        return self.oauth





