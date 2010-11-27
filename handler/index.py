# :set encoding=utf-8
import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.api import users
from datetime import datetime
from helper import *
from model import *
from handler.base import BaseHandler
from handler.base import handle_error

class IndexHandler(BaseHandler):
    @handle_error
    def get(self):
        user = users.get_current_user()
        login_url = ''
        logout_url = ''

        if user:
            logout_url = users.create_logout_url("/")
        else:
            login_url = users.create_login_url("/")

        template_values = {
            'today': datetime.now(),
            'user': user,
            'login_url': login_url,
            'logout_url': logout_url,
            'schema_list': Schema.all().order('-created_at').fetch(1000)
        }
        self.response.out.write(ViewHelper.process('index', template_values))

    @handle_error
    def post(self):
        user = users.get_current_user()
        if not user:
            self.error_response(400, log_msg="user not found")

        name = self.request.get('name')
        origin = self.request.get('origin')
        digit_only = self.request.get('digit-only') == 'on'
        with_api_key = self.request.get('with-api-key') == 'on'

        # TODO このへんでバリデーション

        schema = Schema.create_with_key(
            name=name,
            origin=origin,
            owner=user,
            with_api_key=with_api_key,
            digit_only=digit_only
        )
        self.redirect(schema.url())

