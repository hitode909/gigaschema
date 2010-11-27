import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from datetime import datetime
from helper.view import ViewHelper

class IndexHandler(webapp.RequestHandler):
    def get(self):
        template_values = {
            'today': datetime.now()
            }
        self.response.out.write(ViewHelper.process('index', template_values))
