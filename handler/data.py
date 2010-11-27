import os
import logging
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util, template
from google.appengine.ext.db import BadKeyError
from datetime import datetime
from helper import *
from model import *
from handler.base import BaseHandler
from handler.base import handle_error

class DataHandler(BaseHandler):
    @handle_error
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
        self.response.out.write(ViewHelper.process('data', template_values))

    @handle_error
    def delete(self, owner_name, schema_name, data_key):
        schema = self.get_schema(owner_name, schema_name)
        data = self.get_data(data_key)
        data.delete()
        self.redirect(schema.url())

    @handle_error
    def post(self, owner_name, schema_name, data_key):
        if not self.request.get('delete'):
            self.error_response(400, log_msg="not delete mode")

        return self.delete(owner_name, schema_name, data_key)

class DataJsonHandler(BaseHandler):
    @handle_error
    def get(self, owner_name, schema_name, data_key):
        schema = self.get_schema(owner_name, schema_name)
        data = self.get_data(data_key)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write( ViewHelper.process_data(data.as_hash()))

