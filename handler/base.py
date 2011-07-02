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

    @hook_request
    def head (self,*args, **keywords):
        self.get(*args,**keywords)
        self.response.clear()
        return

    def error_response(self, code, log_msg=""):
        raise HandlerError(code, log_msg=log_msg)

    def before_dispatch(self, *args):
        user = users.get_current_user()
        if user:
            UserHelper.inject_params(user)
            self.user = user

        login_url = ''
        logout_url = ''

        if user:
            logout_url = users.create_logout_url("/")
        else:
            login_url = users.create_login_url("/user")

        self.stash = {
            'h': self,
            'user': user,
            'login_url': login_url,
            'logout_url': logout_url,
        }

        self.data = None
        self.schema = None

    def load_schema(self, owner_name, schema_name, use_cache=False):
        schema = None
        schema_name = urllib.unquote(schema_name).decode('utf-8')
        try:
            schema = Schema.retrieve(owner_name, schema_name, use_cache)
        except BadKeyError, message:
            schema = None
        if not schema:
            self.error_response(404, log_msg="schema not found: " + owner_name + "/" + schema_name)
        self.schema = schema
        self.stash['schema'] = schema
        self.stash['page_schema'] = schema

    def load_data(self, owner_name, schema_name, data_key, use_cache=False):
        data = None
        schema_name = urllib.unquote(schema_name).decode('utf-8')
        try:
            data = Data.retrieve(owner_name, schema_name, data_key, use_cache)
            if data and data.schema and ((UserHelper.extract_user_name(data.schema.owner)) != owner_name or (data.schema.name != schema_name)):
                self.error_response(400, log_msg="")
        except BadKeyError, message:
            data = None
        if not data or data.is_deleted:
            self.error_response(404, log_msg="data not found: " + data_key)
        self.data = data
        self.stash['data'] = data
        self.schema = data.schema
        self.stash['schema'] = data.schema
        self.stash['page_schema'] = data.schema

    def owner(self):
        owner = None
        if self.data:
            owner = self.data.owner
            UserHelper.inject_params(owner)
        elif self.schema:
            owner = self.schema.owner
            UserHelper.inject_params(owner)
        elif self.stash.has_key('owner'):
            owner = self.stash['owner']
            UserHelper.inject_params(owner)
        else:
            owner = self.user

        return owner

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


