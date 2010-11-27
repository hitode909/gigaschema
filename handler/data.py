import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from datetime import datetime
from helper.view import ViewHelper

class DataHandler(webapp.RequestHandler):
    def get(self, owner_name, schema_name, data_key):
        template_values = {
            'owner_name': owner_name,
            'schema_name': schema_name,
            'data_key': data_key,
            }
        self.response.out.write(ViewHelper.process('data', template_values))
