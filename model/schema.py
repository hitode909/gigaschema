from google.appengine.api import users
from google.appengine.ext import db
from time import time
from helper import *
import model
import hashlib

class Schema(db.Model):
    name = db.StringProperty(required=True)
    origin = db.StringProperty()
    digit_only = db.BooleanProperty(default = False)
    api_key = db.StringProperty()
    owner = db.UserProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def key_from_names(klass, owner_name, schema_name):
        return owner_name + '/' + schema_name

    @classmethod
    def create_with_key(klass, **args):
        user = users.get_current_user()

        key_name = klass.key_from_names(
            UserHelper.extract_user_name(args['owner']), 
            args['name']
        )

        schema = klass(
            key_name=key_name,
            name=args['name'],
            origin=args['origin'],
            owner=args['owner'],
            digit_only=args['digit_only'],
        );
        schema.put()

        if args['with_api_key']:
            schema.reset_api_key()

        return schema

    @classmethod
    def retrieve_by_names(klass, owner_name, schema_name):
        key_name = klass.key_from_names(owner_name, schema_name)
        return klass.get_by_key_name(key_name)

    def reset_api_key(self):
        s = hashlib.sha1()
        s.update(str(time()))
        s.update(self.name.encode('utf-8'))
        s.update(self.owner.user_id())
        self.api_key = s.hexdigest()
        self.put();

    def data(self, newer_first=True, group=None, limit=50, offset=0):
        q = model.Data.all()
        q.filter('schema = ', self.key())
        if group:
            q.filter('group = ', group)
        if newer_first:
            q.order('-created_on')
        else:
            q.order('created_on')

        data = q.fetch(limit, offset=offset)
        return data

    def data_has_number(self):
        for item in self.data():
            if item.is_number_item():
                return True
        return False

    def url(self):
        return "/" + UserHelper.extract_user_name(self.owner) + "/" + self.name

    def setting_url(self):
        return "/" + UserHelper.extract_user_name(self.owner) + "/" + self.name + ".setting"

    def slug(self):
        return UserHelper.extract_user_name(self.owner) + "/" + self.name

    def as_hash(self, group=None):
        result = {
            'name': self.name,
            'data': [ data.as_hash() for data in self.data(group=group) ]
        }
        return result

    def current_user_is_owner(self):
        return self.owner.user_id() == self.current_user.user_id()


    def current_user_can_post(self, user = None):
        if not user:
            user = self.current_user
        if not self.api_key:
            return True

        return self.owner.user_id() == user.user_id()
