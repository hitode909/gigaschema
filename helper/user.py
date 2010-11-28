import re
from google.appengine.api import users
class UserHelper:
    @classmethod
    def extract_user_name(klass,user):
        return re.sub('@.*$', '', user.email())

    @classmethod
    def constract_user(klass,user_name):
        return users.User(user_name + '@gmail.com')
