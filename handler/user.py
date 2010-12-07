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

        UserHelper.inject_params(owner)
        self.stash['owner'] = owner
        q = Schema.all()
        q.filter('owner = ', owner)
        q.order('-created_on')

        self.stash['schema_list'] = q.fetch(1000)
        self.response.out.write(ViewHelper.process('user', self.stash))

class UserRedirectHandler(BaseHandler):

    @hook_request
    def get(self):
        if not self.stash['user']:
            self.error_response(403, log_msg="please login")

        self.redirect('/' + UserHelper.extract_user_name(self.stash['user']))
