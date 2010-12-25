import re
import urllib, hashlib
import logging
from google.appengine.api import users
from google.appengine.api import memcache
import model

class UserHelper:
    @classmethod
    def extract_user_name(klass,user):
        return re.sub('@.*$', '', user.email())

    @classmethod
    def constract_user(klass,user_name):
        return users.User(user_name + '@gmail.com')

    @classmethod
    def inject_params(klass, user):
        if not user:
            return

        user.name = klass.extract_user_name(user)
        user.url = '/' + user.name
        user.avatar_url = klass.avatar_url(user)
        user.small_avatar_url = klass.avatar_url(user) + "&s=16"

        user_schemas_key = '/'.join(['user', user.user_id(), 'schema_list'])
        user_schemas = memcache.get(user_schemas_key)
        if user_schemas:
            logging.info('cache hit(user_schemas): ' + user_schemas_key)
        else:
            q = model.schema.Schema.all()
            q.filter('owner = ', user)
            q.order('-updated_on')
            memcache.set(key=user_schemas_key, value=q.fetch(20), time=60*60*1)

        user.schemas = user_schemas

        current_user = users.get_current_user()
        if current_user and user == current_user:
            user.is_current_user = True

        return user

    @classmethod
    def avatar_url(klass, user):
        email = user.email()
        return "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?d=retro"
