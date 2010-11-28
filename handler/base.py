import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from model import *

class HandlerError(Exception):
    def __init__(self, code, log_msg=""):
        self.code = code
        self.log_msg = log_msg

class BaseHandler(webapp.RequestHandler):

    def error_response(self, code, log_msg=""):
        raise HandlerError(code, log_msg=log_msg)

    def get_schema(self, owner_name, schema_name):
        schema = None
        try:
            schema = Schema.retrieve_by_names(owner_name, schema_name)
        except BadKeyError, message:
            schema = None
        if not schema:
            self.error_response(404, log_msg="schema not found: " + owner_name + "/" + schema_name)
        return schema

    def get_data(self, data_key):
        data = None
        try:
            data = Data.get(data_key)
        except BadKeyError, message:
            data = None
        if not data:
            self.error_response(404, log_msg="data not found: " + data_key)
            
        return data

    def set_allow_header(self, schema):
        origin = '*'
        if schema.origin:
            origin = schema.origin

        self.response.headers['Access-Control-Allow-Origin'] = origin
        self.response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'

    def handle_exception(self, exception, debug_mode):
        if isinstance(exception, HandlerError):
            logging.info(exception.log_msg)
            self.error(exception.code)
            self.response.out.write(exception.log_msg)
        else:
            return webapp.RequestHandler.handle_exception(self,exception, debug_mode)


