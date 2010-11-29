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

        q = Schema.all()
        q.filter('owner = ', owner)
        q.order('-created_on')

        self.stash['schema_list'] = q.fetch(1000)
        self.stash['owner_name'] = owner_name
        self.response.out.write(ViewHelper.process('user', self.stash))



