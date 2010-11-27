# :set encoding=utf-8
import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from datetime import datetime
from helper import *
from model import *
from time import time
import hashlib

class IndexHandler(webapp.RequestHandler):
    def get(self):
        template_values = {
            'today': datetime.now()
            }
        self.response.out.write(ViewHelper.process('index', template_values))

    def post(self):
        name = self.request.get('name')
        origin = self.request.get('origin')
        rule = self.request.get('rule')

        # このへんでバリデーション

        s = hashlib.sha1()
        s.update(str(time()))
        s.update(name.encode('utf-8'))
        s.update('user_id')
        api_key = s.hexdigest()

        schema = Schema(
            name=name, 
            origin=origin,
            api_key=api_key,
            rule=rule
        )
        schema.put()

        template_values = {
            "name": name,
            "origin": origin,
            "api_key": api_key,
            "rule": rule,
        }

        # スキーマページにリダイレクト
        self.response.out.write(ViewHelper.process('index', template_values))
