import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.api import users
from model import *
from google.appengine.ext.db import BadKeyError
import urllib
from helper.user import UserHelper

class HandlerError(Exception):
    def __init__(self, code, log_msg=""):
        self.code = code
        self.log_msg = log_msg

def hook_request(orig):
    def decorator(self, *args):
        self.before_dispatch(*args)
        orig(self,*args)
    return decorator

class BaseHandler(webapp.RequestHandler):

    def error_response(self, code, log_msg=""):
        raise HandlerError(code, log_msg=log_msg)

    def before_dispatch(self, *args):
        user = users.get_current_user()
        self.user = user

        login_url = ''
        logout_url = ''

        if user:
            logout_url = users.create_logout_url("/")
        else:
            login_url = users.create_login_url("/")

        self.stash = {
            'user': user,
            'login_url': login_url,
            'logout_url': logout_url,
        }

    def get_schema(self, owner_name, schema_name):
        schema = None
        schema_name = urllib.unquote(schema_name).decode('utf-8')
        try:
            schema = Schema.retrieve_by_names(owner_name, schema_name)
        except BadKeyError, message:
            schema = None
        if not schema:
            self.error_response(404, log_msg="schema not found: " + owner_name + "/" + schema_name)
        return schema

    def get_data(self, owner_name, schema_name, data_key):
        data = None
        try:
            data = Data.get(data_key)
            if data.schema and (UserHelper.extract_user_name(data.schema.owner)) != owner_name or (data.schema.name != schema_name):
                self.error_response(400, log_msg="")
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


