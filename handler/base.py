import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from model import *

class HandlerError(Exception):
    def __init__(self, code, log_msg=""):
        self.code = code
        self.log_msg = log_msg
        

def handle_error(orig):
    def decorator(self,*args):
        try:
            orig(self, *args)
        except RequestError, e:
            logging.info(e.log_msg)
            self.error(e.code)
            self.response.out.write( self.response.http_status_message(e.code))
    return decorator

class BaseHandler(webapp.RequestHandler):

    def error_response(self, code, log_msg=""):
        raise HandleError(code, log_msg=log_msg)

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

