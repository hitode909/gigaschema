import os
import logging
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util, template
from datetime import datetime
from helper import *
from model import *
from handler.base import BaseHandler
from handler.base import hook_request

class DataHandler(BaseHandler):

    @hook_request
    def get(self, owner_name, schema_name, data_key):
        schema = self.get_schema(owner_name, schema_name)
        data = self.get_data(data_key)

        template_values = {
            'owner_name': owner_name,
            'schema_name': schema_name,
            'data_key': data_key,
            'data': data,       # TODO
            'data_url': self.request.path # TODO = data.url
        }
        self.stash.update(template_values)
        self.response.out.write(ViewHelper.process('data', self.stash))

    @hook_request
    def delete(self, owner_name, schema_name, data_key):
        schema = self.get_schema(owner_name, schema_name)
        if schema.api_key and schema.api_key != self.request.get('api_key'):
            self.error_response(403, log_msg="invlid api")

        data = self.get_data(data_key)
        data.delete()
        self.set_allow_header(schema)
        self.redirect(schema.url())

    @hook_request
    def post(self, owner_name, schema_name, data_key):
        if not self.request.get('delete'):
            self.error_response(400, log_msg="not delete mode")

        return self.delete(owner_name, schema_name, data_key)

    @hook_request
    def options(self, owner_name, schema_name, data_key):
        schema = self.get_schema(owner_name, schema_name)
        self.set_allow_header(schema)
        self.response.out.write('options')

class DataJsonHandler(BaseHandler):
    @hook_request
    def get(self, owner_name, schema_name, data_key):
        schema = self.get_schema(owner_name, schema_name)
        data = self.get_data(data_key)

        self.set_allow_header(schema)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write( ViewHelper.process_data(data.as_hash()))

