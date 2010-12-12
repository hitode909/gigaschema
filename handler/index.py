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
from handler.base import hook_request

class IndexHandler(BaseHandler):

    @hook_request
    def get(self):
        if not self.stash['user']:
            self.response.out.write(ViewHelper.process('index', self.stash))
            return

        user = self.stash['user']
        self.stash['owner'] = user

        q = Data.all();
        q.filter('owner = ', user)
        q.order('-created_on')
        user.data = q.fetch(1000)

        self.response.out.write(ViewHelper.process('user', self.stash))

    @hook_request
    def post(self):
        if not self.user:
            self.error_response(403, log_msg="user not found")

        name = self.request.get('name')
        origin = self.request.get('origin')
        digit_only = self.request.get('digit-only') == 'on'
        with_api_key = self.request.get('with-api-key') == 'on'

        if not Schema.validate_name(name):
            self.error_response(400, log_msg="name must not include '.' or '/'")

        if not Schema.validate_origin(origin):
            self.error_response(400, log_msg="Access-Control-Allow-Origin: <origin> | *")

        schema = Schema.create_with_key(
            name=name,
            origin=origin,
            owner=self.user,
            with_api_key=with_api_key,
            digit_only=digit_only
        )
        self.redirect(schema.url())

class CreateHandler(BaseHandler): # create.py......

    @hook_request
    def get(self):
        self.response.out.write(ViewHelper.process('create', self.stash))

