# :set encoding=utf-8
import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from helper import *
from model import *
from handler.base import BaseHandler
from handler.base import hook_request

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
