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

class SchemaHandler(BaseHandler):

    @hook_request
    def get(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name)
        schema.current_user = self.user

        group = self.request.get('group') or None

        self.stash['schema'] = schema
        self.stash['schema_data'] = schema.data(group = group)

        self.response.out.write(ViewHelper.process('schema', self.stash))

    @hook_request
    def post(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name)
        if schema.api_key and schema.api_key != self.request.get('api_key'):
            self.error_response(403, log_msg="invlid api")


        value = self.request.get('value') or ""
        if not schema.validate_value(value):
            self.error_response(400, log_msg="bad value")

        group = self.request.get('group') or None
        if not Data.validate_group(group):
            self.error_response(400, log_msg="group must not include '.' or '/'")


        data = Data.create(schema, group=group, value=value)
        self.redirect(schema.url())

class SchemaSettingHandler(BaseHandler):

    @hook_request
    def get(self, owner_name, schema_name):
        if not self.user:
            self.error_response(403, log_msg="no user")
        schema = self.get_schema(owner_name, schema_name)
        if self.user.user_id() != schema.owner.user_id():
            self.error_response(403, log_msg="invalid user")

        self.stash['schema'] = schema
        self.response.out.write(ViewHelper.process('schema_setting', self.stash))

    @hook_request
    def post(self, owner_name, schema_name):
        if not self.user:
            self.error_response(403, log_msg="no user")
        schema = self.get_schema(owner_name, schema_name)
        if self.user.user_id() != schema.owner.user_id():
            self.error_response(403, log_msg="invalid user")

        # origin=*
        # digit_only=''|on
        # reset_api_key=''|1
        if self.request.get('reset_api_key'):
            schema.reset_api_key()
        if self.request.get('remove_api_key'):
            schema.api_key = None
        if self.request.get('origin'):
            schema.origin = self.request.get('origin')
        if self.request.get('digit_only'):
            digit_only = (self.request.get('digit_only') == '1')
            schema.digit_only = digit_only
        schema.put()

        self.redirect(schema.setting_url())

class SchemaJsonHandler(BaseHandler):

    @hook_request
    def get(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name)
        group = self.request.get('group') or None

        self.set_allow_header(schema)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write( ViewHelper.process_data(schema.as_hash(group=group)) )

    @hook_request
    def options(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name)

        self.set_allow_header(schema)
        self.response.out.write('options')
