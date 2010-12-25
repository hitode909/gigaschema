# :set encoding=utf-8
import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.api import memcache
from helper import *
from model import *
from handler.base import BaseHandler
from handler.base import hook_request
from django.utils import feedgenerator

class UserHandler(BaseHandler):

    @hook_request
    def get(self, owner_name):
        owner = UserHelper.constract_user(owner_name)
        if not owner_name:
            self.error_response(404, log_msg="user not found")

        if self.stash['user']:
            owner.is_current_user = self.stash['user'].email() == owner.email()
        else:
            owner.is_current_user = True

        limit = 20
        page = int(self.request.get('page') or 1)
        page = 1 if page < 1 else page
        offset = limit * (page - 1)
        data_list = Data.all().filter('is_deleted =', False).filter('owner = ', owner).order('-created_on').fetch(limit+1, offset)

        self.stash['pager'] = {
            'url': '/' + owner_name + '/',
            'data': data_list[0:limit],
            'page': page,
            'has_next': len(data_list) > limit,
            'next_page': page + 1,
            'has_prev': page > 1,
            'prev_page': page - 1,
        }

        self.stash['owner'] = owner

        self.response.out.write(ViewHelper.process('user', self.stash))

class UserRedirectHandler(BaseHandler):

    @hook_request
    def get(self):
        if not self.stash['user']:
            self.error_response(403, log_msg="please login")

        self.redirect('/' + UserHelper.extract_user_name(self.stash['user']))

class UserFeedHandler(BaseHandler):
    @hook_request
    def get(self, owner_name):
        owner = UserHelper.constract_user(owner_name)
        if not owner_name:
            self.error_response(404, log_msg="user not found")

        user_feed_key = '/'.join(['schema', owner_name, 'feed']);
        user_feed = memcache.get(user_feed_key)

        if user_feed:
            logging.info('cache hit(schema.feed): ' + user_feed_key)
        else:
            data_list = Data.all().filter('is_deleted =', False).filter('owner = ', owner).order('-created_on').fetch(20, 0)

            feed = feedgenerator.Atom1Feed(
                title = owner_name + ' - GIGA SCHEMA',
                link = 'http://gigaschema.appspot.com/' + owner_name,
                description = "",
                language = 'ja',
                author_name = owner_name,
            )

            for data in data_list:
                feed.add_item(
                    title =('/'.join([owner_name, data.schema.name, str(data.key())])) + ' - GIGA SCHEMA',
                    unique_id = '/'.join([owner_name, data.schema.name, str(data.key())]),
                    link = 'http://gigaschema.appspot.com' + data.url(),
                    description = data.value_as_html(),
                    pubdate = data.created_on,
                )
            user_feed = feed.writeString('utf-8')
            memcache.set(key=user_feed_key, value=user_feed, time=60*30)
        self.response.headers['Content-Type'] = 'application/atom+xml;type=feed;charset="utf-8"'
        self.response.out.write(user_feed)
