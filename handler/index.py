# :set encoding=utf-8
import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.api import users
from google.appengine.api import memcache
from datetime import datetime
from helper import *
from model import *
from handler.base import BaseHandler
from handler.base import hook_request

class IndexHandler(BaseHandler):

    @hook_request
    def get(self):
        data_list_key = '/'.join(['index', 'data_list']);
        data_list = memcache.get(key=data_list_key)
        if not data_list :
            q = Data.all();
            q.order('-created_on')
            data_list = q.fetch(20)
            memcache.set(key=data_list_key, value=data_list, time=60*1)

        self.stash['data_list'] = data_list

        schema_list_key = '/'.join(['index', 'schema_list']);
        schema_list = memcache.get(key=schema_list_key)
        if not schema_list :
            q = Schema.all();
            q.order('-updated_on')
            schema_list = q.fetch(20)
            memcache.set(key=schema_list_key, value=schema_list, time=60*1)


        self.stash['schema_list'] = schema_list

        self.response.out.write(ViewHelper.process('index', self.stash))
        return


    @hook_request
    def post(self):
        if not self.user:
            self.error_response(403, log_msg="user not found")

        name = self.request.get('name')
        origin = self.request.get('origin')
        with_api_key = self.request.get('with-api-key') == 'on'

        if not Schema.validate_name(name):
            self.error_response(400, log_msg="name must not include '.' or '/'")

        if not Schema.validate_origin(origin):
            self.error_response(400, log_msg="Access-Control-Allow-Origin: <origin> | *")

        schema = Schema.create_with_key(
            name=name,
            origin=origin,
            owner=self.user,
            with_api_key=with_api_key
        )
        self.redirect(schema.url())

class CreateHandler(BaseHandler):

    @hook_request
    def get(self):
        self.response.out.write(ViewHelper.process('create', self.stash))

class HelpHandler(BaseHandler):

    @hook_request
    def get(self):
        self.response.out.write(ViewHelper.process('help', self.stash))

