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
            'owner_name': owner_name,
            'schema_name': schema_name,
            'schema': schema,
            'schema_url': self.request.path # TODO = shema.url
        }
        self.response.out.write(ViewHelper.process('schema', template_values))

    def post(self, owner_name, schema_name):
        schema = Schema.retrieve_by_names(owner_name, schema_name)
        if not schema:
            self.redirect('/')

        value = self.request.get('value')
        data = Data.create(schema, value)
        self.redirect(self.request.path)

class SchemaSettingHandler(webapp.RequestHandler):
    def get(self, owner_name, schema_name):
        template_values = {
            'owner_name': owner_name,
            'schema_name': schema_name,
            'schema': None,        # TODO
            'schema_setting_url': self.request.path # TODO = shema.setting_url
            }
        self.response.out.write(ViewHelper.process('schema_setting', template_values))

    def post(self, owner_name, schema_name):
        # origin=*
        # permission=public|private
        # reset_api_key=0|1
        self.response.out.write("setting changed")

class SchemaJsonHandler(webapp.RequestHandler):
    def get(self, owner_name, schema_name):
        self.response.out.write("schema json get")
