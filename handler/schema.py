import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.api import users
from datetime import datetime
from helper import *
from model import *
from handler.base import BaseHandler
from handler.base import hook_request
import logging

class SchemaHandler(BaseHandler):

    @hook_request
    def get(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name, use_cache = True)
        schema.current_user = self.user

        group = self.request.get('group') or None
        page = int(self.request.get('page') or 1)
        page = 1 if page < 1 else page

        self.stash['schema'] = schema
        self.stash['pager'] = schema.data_at_page(page=page, group = group, per_page=50, use_cache=True)
        self.response.out.write(ViewHelper.process('schema', self.stash))

    @hook_request
    def delete(self, owner_name, schema_name):
        if not self.user:
            self.error_response(403, log_msg="no user")
        schema = self.get_schema(owner_name, schema_name)
        if self.user.user_id() != schema.owner.user_id():
            self.error_response(403, log_msg="invalid user")


        schema.clear_data_cache_all()
        schema.delete_with_data()
        self.redirect('/')

    @hook_request
    def post(self, owner_name, schema_name):
        if self.request.get('delete'):
            return self.delete(owner_name, schema_name);

        schema = self.get_schema(owner_name, schema_name)
        if schema.api_key and schema.api_key != self.request.get('api_key'):
            self.error_response(403, log_msg="invlid api")

        values = self.request.get_all('value') or []
        for value in values:
            if not schema.validate_value(value):
                self.error_response(400, log_msg="bad value")

        group = self.request.get('group') or None
        if not Data.validate_group(group):
            self.error_response(400, log_msg="group must not include '.' or '/'")

        data = Data.create_multi(schema, group=group, values=values)
        logging.info('before clear')
        schema.clear_data_cache_all();
        logging.info('after clear')
        self.redirect(schema.url())

class SchemaSettingHandler(BaseHandler):

    @hook_request
    def get(self, owner_name, schema_name):
        if not self.user:
            self.error_response(403, log_msg="no user")
        schema = self.get_schema(owner_name, schema_name)
        if self.user.user_id() != schema.owner.user_id():
            self.error_response(403, log_msg="invalid user")

        self.stash['schema'] = schema
        self.response.out.write(ViewHelper.process('schema_setting', self.stash))

    @hook_request
    def post(self, owner_name, schema_name):
        if not self.user:
            self.error_response(403, log_msg="no user")
        schema = self.get_schema(owner_name, schema_name)
        if self.user.user_id() != schema.owner.user_id():
            self.error_response(403, log_msg="invalid user")

        # origin=*
        # reset_api_key=''|1
        if self.request.get('reset_api_key'):
            schema.reset_api_key()
        if self.request.get('remove_api_key'):
            schema.api_key = None
        if self.request.get('origin') != None:
            origin = self.request.get('origin')
            if not Schema.validate_origin(origin):
                self.error_response(400, log_msg="Access-Control-Allow-Origin: <origin> | *")
            schema.origin = self.request.get('origin')
        schema.put()

        self.redirect(schema.setting_url())

class SchemaJsonHandler(BaseHandler):

    @hook_request
    def get(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name, use_cache = True)
        group = self.request.get('group') or None
        page = int(self.request.get('page') or 1)
        page = 1 if page < 1 else page

        self.set_allow_header(schema)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write( ViewHelper.process_data(schema.as_hash(group=group, page=page, per_page=200, use_cache=True)) )

    @hook_request
    def post(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name)
        if schema.api_key and schema.api_key != self.request.get('api_key'):
            self.error_response(403, log_msg="invalid api")

        values = self.request.get_all('value') or []
        for value in values:
            if not schema.validate_value(value):
                self.error_response(400, log_msg="bad value")

        group = self.request.get('group') or None
        if not Data.validate_group(group):
            self.error_response(400, log_msg="group must not include '.' or '/'")

        data = Data.create_multi(schema, group=group, values=values)
        schema.clear_data_cache_all();
        self.set_allow_header(schema)
        self.response.out.write( ViewHelper.process_data(schema.as_hash_with_data(data=data)) )

    @hook_request
    def options(self, owner_name, schema_name):
        schema = self.get_schema(owner_name, schema_name)

        self.set_allow_header(schema)
        self.response.out.write('options')




# /schema
class RecentSchemaHandler(BaseHandler):

    @hook_request
    def get(self):
        limit = 50
        page = int(self.request.get('page') or 1)
        page = 1 if page < 1 else page
        offset = limit * (page - 1)
        schema_list = Schema.all().order('-created_on').fetch(limit+1, offset)

        self.stash['pager'] = {
            'url': '/schema',
            'data': schema_list[0:limit],
            'page': page,
            'has_next': len(schema_list) > limit,
            'next_page': page + 1,
            'has_prev': page > 1,
            'prev_page': page - 1,
        }

        self.response.out.write(ViewHelper.process('recent_schema', self.stash))
