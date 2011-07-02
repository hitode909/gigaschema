import os
import logging
from google.appengine.api import memcache
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util, template
from django.utils import simplejson
from datetime import datetime
from helper import *
from model import *
from handler.base import BaseHandler
from handler.base import hook_request

class DataHandler(BaseHandler):

    @hook_request
    def get(self, owner_name, schema_name, data_key):
        self.load_data(owner_name, schema_name, data_key, use_cache = True)

        self.response.out.write(ViewHelper.process('data', self.stash))

    @hook_request
    def delete(self, owner_name, schema_name, data_key):
        self.load_data(owner_name, schema_name, data_key)
        if not self.schema.current_user_can_delete() and self.schema.api_key and self.schema.api_key != self.request.get('api_key'):
            self.error_response(403, log_msg="invalid api")
        self.data.is_deleted = True
        self.data.put()

        # self.data.delete()
        self.schema.clear_data_cache_all();
        self.set_allow_header(self.schema)
        self.redirect(self.schema.url())

    @hook_request
    def post(self, owner_name, schema_name, data_key):
        if not self.request.get('delete'):
            self.error_response(400, log_msg="not delete mode")

        return self.delete(owner_name, schema_name, data_key)

    @hook_request
    def options(self, owner_name, schema_name, data_key):
        self.load_data(owner_name, schema_name, data_key)
        self.set_allow_header(self.schema)
        self.response.out.write('options')

class DataJsonHandler(BaseHandler):
    @hook_request
    def get(self, owner_name, schema_name, data_key):
        self.load_data(owner_name, schema_name, data_key, use_cache = True)

        self.set_allow_header(self.schema)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write( ViewHelper.process_data(self.data.as_hash()))

class DataMediaHandler(BaseHandler):
    @hook_request
    def get(self, owner_name, schema_name, data_key, data_type):
        self.load_data(owner_name, schema_name, data_key)
        self.set_allow_header(self.schema)

        info = self.data.blob_info()
        if not info:
            self.error_response(400, log_msg="not blob")

        self.response.headers['Content-Type'] = info['content-type']
        self.response.out.write(info['blob'])

    @hook_request
    def options(self, owner_name, schema_name, data_key, data_type):
        self.load_data(owner_name, schema_name, data_key)
        self.set_allow_header(self.schema)
        self.response.out.write('options')

class DataValueHandler(BaseHandler):
    @hook_request
    def get(self, owner_name, schema_name, data_key):
        self.load_data(owner_name, schema_name, data_key)
        self.set_allow_header(self.schema)

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(self.data.value)

    @hook_request
    def options(self, owner_name, schema_name, data_key):
        self.load_data(owner_name, schema_name, data_key)
        self.set_allow_header(self.schema)
        self.response.out.write('options')


# /data
class RecentDataHandler(BaseHandler):

    @hook_request
    def get(self):
        limit = 50
        page = int(self.request.get('page') or 1)
        page = 1 if page < 1 else page
        offset = limit * (page - 1)

        data_list = []
        key = "/".join(['data', 'recent', str(page)])
        if page == 1:
            json = memcache.get(key)
            if json:
                data_keys_list = simplejson.loads(json)
                for data_keys in data_keys_list:
                    data_keys.append(True)
                    d = Data.retrieve(*data_keys)
                    if d:
                        data_list.append(d)

        if len(data_list) == 0:
            data_list = Data.all().filter('is_deleted =', False ).order('-created_on').fetch(limit+1, offset)
            data_keys_list = []
            for data in data_list:
                data_keys_list.append([
                    UserHelper.extract_user_name(data.schema.owner),
                    data.schema.name,
                    str(data.key()),
                ])
            json = simplejson.dumps(data_keys_list)
            if page == 1:
                memcache.set(key=key, value=json, time=60*60*1)

        self.stash['pager'] = {
            'url': '/data',
            'data': data_list[0:limit],
            'page': page,
            'has_next': len(data_list) > limit,
            'next_page': page + 1,
            'has_prev': page > 1,
            'prev_page': page - 1,
        }

        self.response.out.write(ViewHelper.process('recent_data', self.stash))
