from google.appengine.api import users
from google.appengine.ext import db
from time import time
from helper import *
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
        if args['with_api_key']:
            schema.reset_api_key()

        schema.put()

        return schema

    @classmethod
    def retrieve_by_names(klass, owner_name, schema_name):
        key_name = klass.key_from_names(owner_name, schema_name)
        return klass.get_by_key_name(key_name)

    def reset_api_key(self):
        s = hashlib.sha1()
        s.update(str(time()))
        s.update(self.name.encode('utf-8'))
        s.update(self.owener.user_id())
        self.api_key_value = s.hexdigest()
        self.put();

    def data(self, newer_first=True):
        order_dir = 'ASC'
        if newer_first:
            order_dir = 'DESC'

        q = db.GqlQuery("SELECT * FROM Data " + 
                        "WHERE schema = :1 " + 
                        "ORDER BY datetime " + order_dir, self.key())
        data = q.fetch(100)
        return data

    def url(self):
        return "/" + UserHelper.extract_user_name(self.owner) + "/" + self.name

    def setting_url(self):
        return "/" + UserHelper.extract_user_name(self.owner) + "/" + self.name + ".setting"

    def slug(self):
        return UserHelper.extract_user_name(self.owner) + "/" + self.name

    def as_hash(self):
        result = {
            'name': self.name,
            'data': [ data.as_hash() for data in self.data() ]
        }
        return result




