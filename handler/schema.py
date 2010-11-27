import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from datetime import datetime
from helper import *

class SchemaHandler(webapp.RequestHandler):
    def get(self, owner_name, schema_name):
        template_values = {
            'owner_name': owner_name,
            'schema_name': schema_name,
            }
        self.response.out.write(ViewHelper.process('schema', template_values))
