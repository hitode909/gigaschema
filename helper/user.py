import re
import urllib, hashlib
from google.appengine.api import users

class UserHelper:
    @classmethod
    def extract_user_name(klass,user):
        return re.sub('@.*$', '', user.email())

    @classmethod
    def constract_user(klass,user_name):
        return users.User(user_name + '@gmail.com')

    @classmethod
    def inject_params(klass, user):
        user.name = klass.extract_user_name(user)
        user.avatar_url = klass.avatar_url(user)
        user.small_avatar_url = klass.avatar_url(user) + "&s=16"
        return user

    @classmethod
    def avatar_url(klass, user):
        email = user.email()
        return "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?d=retro"
