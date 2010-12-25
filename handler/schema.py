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
import random

class SchemaHandler(BaseHandler):

    @hook_request
    def get(self, owner_name, schema_name):
        self.load_schema(owner_name, schema_name, use_cache = True)

        group = self.request.get('group') or None
        page = int(self.request.get('page') or 1)
        page = 1 if page < 1 else page

        self.stash['pager'] = self.schema.data_at_page(page=page, group = group, per_page=50, use_cache=True)
        self.response.out.write(ViewHelper.process('schema', self.stash))

    @hook_request
    def delete(self, owner_name, schema_name):
        if not self.user:
            self.error_response(403, log_msg="no user")
        self.load_schema(owner_name, schema_name)
        if self.user != self.schema.owner:
            self.error_response(403, log_msg="invalid user")

        self.schema.clear_data_cache_all()
        self.schema.delete_with_data()
        self.redirect('/')

    @hook_request
    def post(self, owner_name, schema_name):
        if self.request.get('delete'):
            return self.delete(owner_name, schema_name);

        self.load_schema(owner_name, schema_name)
        if self.schema.api_key and self.schema.api_key != self.request.get('api_key'):
            self.error_response(403, log_msg="invlid api")

        values = self.request.get_all('value') or []
        for value in values:
            if not self.schema.validate_value(value):
                self.error_response(400, log_msg="bad value")

        group = self.request.get('group') or None
        if not Data.validate_group(group):
            self.error_response(400, log_msg="group must not include '.' or '/'")

        data = Data.create_multi(self.schema, group=group, values=values)
        logging.info('before clear')
        self.schema.clear_data_cache_all()
        logging.info('after clear')
        self.schema.updated_now()
        self.redirect(self.schema.url())

class SchemaSettingHandler(BaseHandler):

    @hook_request
    def get(self, owner_name, schema_name):
        if not self.user:
            self.error_response(403, log_msg="no user")
        self.load_schema(owner_name, schema_name)
        if self.user != self.schema.owner:
            self.error_response(403, log_msg="invalid user")

        self.response.out.write(ViewHelper.process('schema_setting', self.stash))

    @hook_request
    def post(self, owner_name, schema_name):
        if not self.user:
            self.error_response(403, log_msg="no user")
        self.load_schema(owner_name, schema_name)
        if self.user != self.schema.owner:
            self.error_response(403, log_msg="invalid user")

        # origin=*
        # api_key_method=use|not_use|reset
        if self.request.get('api_key_method') == 'use' and not self.schema.api_key:
            self.schema.reset_api_key()
        if self.request.get('api_key_method') == 'reset':
            self.schema.reset_api_key()
        if self.request.get('api_key_method') == 'not_use':
            self.schema.api_key = None
        if self.request.get('origin') != None:
            origin = self.request.get('origin')
            if not Schema.validate_origin(origin):
                self.error_response(400, log_msg="Access-Control-Allow-Origin: <origin> | *")
            self.schema.origin = self.request.get('origin')
        self.schema.put()

        self.redirect(self.schema.setting_url())

class SchemaJsonHandler(BaseHandler):

    @hook_request
    def get(self, owner_name, schema_name):
        self.load_schema(owner_name, schema_name, use_cache = True)
        group = self.request.get('group') or None
        page = int(self.request.get('page') or 1)
        page = 1 if page < 1 else page

        self.set_allow_header(self.schema)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write( ViewHelper.process_data(self.schema.as_hash(group=group, page=page, per_page=200, use_cache=True)) )

    @hook_request
    def post(self, owner_name, schema_name):
        self.load_schema(owner_name, schema_name)
        if self.schema.api_key and self.schema.api_key != self.request.get('api_key'):
            self.error_response(403, log_msg="invalid api")

        values = self.request.get_all('value') or []
        for value in values:
            if not self.schema.validate_value(value):
                self.error_response(400, log_msg="bad value")

        group = self.request.get('group') or None
        if not Data.validate_group(group):
            self.error_response(400, log_msg="group must not include '.' or '/'")

        data = Data.create_multi(self.schema, group=group, values=values)
        self.schema.clear_data_cache_all();
        self.set_allow_header(self.schema)
        self.response.out.write( ViewHelper.process_data(self.schema.as_hash_with_data(data=data)) )

    @hook_request
    def options(self, owner_name, schema_name):
        self.load_schema(owner_name, schema_name)

        self.set_allow_header(self.schema)
        self.response.out.write('options')


class SchemaRandomJsonHandler(BaseHandler):
    @hook_request
    def get(self, owner_name, schema_name):
        self.load_schema(owner_name, schema_name, use_cache = True)
        q = Data.all()
        q.filter('schema = ', self.schema.key())

        group = self.request.get('group') or None
        if group:
            q.filter('group = ', group)

        data = q.fetch(1, random.randint(0, q.count() - 1))[0]

        self.set_allow_header(self.schema)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write( ViewHelper.process_data(data.as_hash()))

    @hook_request
    def options(self, owner_name, schema_name):
        self.load_schema(owner_name, schema_name)

        self.set_allow_header(self.schema)
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
