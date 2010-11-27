import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from datetime import datetime
from helper import *
from model import *
from handler.base import BaseHandler
from handler.base import handle_error

class SchemaHandler(BaseHandler):

    @handle_error
    def get(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name)

        template_values = {
            'schema': schema,
            'data': ViewHelper.process_data(schema.as_hash())
        }
        self.response.out.write(ViewHelper.process('schema', template_values))

    @handle_error
    def post(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name)
        if schema.api_key and schema.api_key != self.request.get('api_key'):
            self.error_response(403, log_msg="invlid api")

        value = self.request.get('value')
        data = Data.create(schema, value)
        self.redirect(schema.url())

class SchemaSettingHandler(BaseHandler):
    @handle_error
    def get(self, owner_name, schema_name):
        user = users.get_current_user();
        if not user:
            self.error_response(403, log_msg="no user")
        schema = self.get_schema(owner_name, schema_name)
        if user.user_id() != schema.owner.user_id():
            self.error_response(403, log_msg="invalid user")

        template_values = {
            'schema': schema
        }
        self.response.out.write(ViewHelper.process('schema_setting', template_values))

    @handle_error
    def post(self, owner_name, schema_name):
        user = users.get_current_user();
        if not user:
            self.error_response(403, log_msg="no user")
        schema = self.get_schema(owner_name, schema_name)
        if user.user_id() != schema.owner.user_id():
            self.error_response(403, log_msg="invalid user")

        # origin=*
        # digit_only=0|!
        # reset_api_key=0|1
        if self.request.get('reset_api_key'):
            schema.reset_api_key()
        if self.request.get('remove_api_key'):
            schema.api_key = None
        if self.request.get('origin'):
            schema.origin = self.request.get('origin')
        if self.request.get('digit_only'):
            schema.digit_only = self.request.get('digit_only')

        self.redirect(schema.url())

class SchemaJsonHandler(BaseHandler):
    @handle_error
    def get(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name)

        self.set_allow_header(schema)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write( ViewHelper.process_data(schema.as_hash()) )

    @handle_error
    def options(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name)

        self.set_allow_header(schema)
        self.response.out.write('options')
