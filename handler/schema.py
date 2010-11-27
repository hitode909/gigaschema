import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from datetime import datetime
from helper import *
from model import *

class SchemaHandler(webapp.RequestHandler):
    def get(self, owner_name, schema_name):
        schema = Schema.retrieve_by_names(owner_name, schema_name)
        if not schema:
            self.redirect('/')

        template_values = {
            'schema': schema,
            'data': ViewHelper.process_data(schema.as_hash())
        }
        self.response.out.write(ViewHelper.process('schema', template_values))

    def post(self, owner_name, schema_name):
        schema = Schema.retrieve_by_names(owner_name, schema_name)
        if not schema:
            self.redirect('/')

        value = self.request.get('value')
        data = Data.create(schema, value)
        self.redirect(schema.url())

class SchemaSettingHandler(webapp.RequestHandler):
    def get(self, owner_name, schema_name):
        schema = Schema.retrieve_by_names(owner_name, schema_name)
        template_values = {
            'schema': schema
        }
        self.response.out.write(ViewHelper.process('schema_setting', template_values))

    def post(self, owner_name, schema_name):
        schema = Schema.retrieve_by_names(owner_name, schema_name)
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

class SchemaJsonHandler(webapp.RequestHandler):
    def get(self, owner_name, schema_name):
        schema = Schema.retrieve_by_names(owner_name, schema_name)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write( ViewHelper.process_data(schema.as_hash()) )

