# :set encoding=utf-8
import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.api import users
from google.appengine.api import memcache
from datetime import datetime
from helper import *
from model import *
from handler.base import BaseHandler
from handler.base import hook_request
from django.utils import feedgenerator

class IndexHandler(BaseHandler):

    @hook_request
    def get(self):
        q = Data.all();
        q.filter('is_deleted =', False)
        q.order('-created_on')
        data_list = q.fetch(20)
        self.stash['data_list'] = data_list

        q = Schema.all();
        q.order('-updated_on')
        schema_list = q.fetch(20)
        self.stash['schema_list'] = schema_list

        self.response.out.write(ViewHelper.process('index', self.stash))
        return


    @hook_request
    def post(self):
        if not self.user:
            self.error_response(403, log_msg="user not found")

        name = self.request.get('name')
        origin = self.request.get('origin')
        with_api_key = self.request.get('with-api-key') == 'on'

        if not Schema.validate_name(name):
            self.error_response(400, log_msg="name must not include '.' or '/'")

        if not Schema.validate_origin(origin):
            self.error_response(400, log_msg="Access-Control-Allow-Origin: <origin> | *")

        schema = Schema.create_with_key(
            name=name,
            origin=origin,
            owner=self.user,
            with_api_key=with_api_key
        )
        self.redirect(schema.url())

class FeedHandler(BaseHandler):
    @hook_request
    def get(self):
        recent_feed_key = '/'.join(['index', 'data_list', 'feed']);
        recent_feed = memcache.get(recent_feed_key)
        if recent_feed:
            logging.info('cache hit(recent_feed)')
        else:
            q = Data.all();
            q.filter('is_deleted =', False)
            q.order('-created_on')
            data_list = q.fetch(20)

            feed = feedgenerator.Atom1Feed(
                title = 'GIGA SCHEMA - recent data',
                link = 'http://gigaschema.appspot.com',
                description = "",
                language = 'ja',
            )

            for data in data_list:
                feed.add_item(
                    title ='GIGA SCHEMA - ' +  ('/'.join([data.owner.nickname(), data.schema.name, str(data.key())])),
                    unique_id = '/'.join([data.owner.nickname(), data.schema.name, str(data.key())]),
                    link = 'http://gigaschema.appspot.com' + data.url(),
                    description = data.value_as_html(),
                    pubdate = data.created_on,
                )
            recent_feed = feed.writeString('utf-8')
            memcache.set(key=recent_feed_key, value=recent_feed, time=60*30)
        self.response.headers['Content-Type'] = 'application/atom+xml;type=feed;charset="utf-8"'
        self.response.out.write(recent_feed)

class CreateHandler(BaseHandler):

    @hook_request
    def get(self):
        self.response.out.write(ViewHelper.process('create', self.stash))

class HelpHandler(BaseHandler):

    @hook_request
    def get(self):
        self.response.out.write(ViewHelper.process('help', self.stash))

