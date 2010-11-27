import os
import logging
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util, template
from google.appengine.ext.db import BadKeyError
from datetime import datetime
from helper import *
from model import *

class DataHandler(webapp.RequestHandler):
    def get(self, owner_name, schema_name, data_key):
        schema = Schema.retrieve_by_names(owner_name, schema_name)
        if not schema:
            logging.info("schema not found " + schema_name)
            self.response.out.write(self.response.http_status_message(404))
            return

        data = Data.get(data_key)
        if not data:
            logging.info("data not found " + data_key)
            self.response.out.write(self.response.http_status_message(404))
            return

        template_values = {
            'owner_name': owner_name,
            'schema_name': schema_name,
            'data_key': data_key,
            'data': data,       # TODO
            'data_url': self.request.path # TODO = data.url
            }
        self.response.out.write(ViewHelper.process('data', template_values))

    def delete(self, owner_name, schema_name, data_key):
        schema = Schema.retrieve_by_names(owner_name, schema_name)
        if not schema:
            logging.info("schema not found " + schema_name)
            self.response.out.write(self.response.http_status_message(404))
            return

        data = Data.get(data_key)
        if not data:
            logging.info("data not found " + data_key)
            self.response.out.write(self.response.http_status_message(404))
            return

        data.delete()
        self.redirect(schema.url())

    def post(self, owner_name, schema_name, data_key):
        if not self.request.get('delete'):
            self.response.out.write(self.response.http_status_message(400))
            return

        return self.delete(owner_name, schema_name, data_key)

class DataJsonHandler(webapp.RequestHandler):
    def get(self, owner_name, schema_name, data_key):
        try:
            schema = Schema.retrieve_by_names(owner_name, schema_name)
            if not schema:
                logging.info("schema not found " + schema_name)
                self.response.out.write(self.response.http_status_message(404))
                return

            data = Data.get(data_key)
            if not data:
                logging.info("data not found " + data_key)
                self.response.out.write(self.response.http_status_message(404))
                return

        except BadKeyError, message:
            logging.info(message)
            self.error(404)
            self.response.out.write(self.response.http_status_message(404))
            return

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write( ViewHelper.process_data(data.as_hash()))

