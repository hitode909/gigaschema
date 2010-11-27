import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from datetime import datetime
from helper import *

class DataHandler(webapp.RequestHandler):
    def get(self, owner_name, schema_name, data_key):
        template_values = {
            'owner_name': owner_name,
            'schema_name': schema_name,
            'data_key': data_key,
            'data': None,       # TODO
            'data_url': self.request.path # TODO = data.url
            }
        self.response.out.write(ViewHelper.process('data', template_values))

    def delete(self, owner_name, schema_name, data_key):
        self.response.out.write(data_key + " deleted")

    def post(self, owner_name, schema_name, data_key):
        if not self.request.get('delete'):
            self.response.out.write(self.response.http_status_message(400))
            return

        return self.delete(owner_name, schema_name, data_key)
