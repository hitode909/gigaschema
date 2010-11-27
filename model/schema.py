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

        api_key_value = None
        if args['with_api_key']:
            s = hashlib.sha1()
            s.update(str(time()))
            s.update(args['name'].encode('utf-8'))
            s.update(user.user_id())
            api_key_value = s.hexdigest()

        schema = klass(
            key_name=key_name,
            name=args['name'],
            origin=args['origin'],
            owner=args['owner'],
            api_key=api_key_value,
            digit_only=args['digit_only'],
        );
        schema.put()

        return schema

    @classmethod
    def retrieve_by_names(klass, owner_name, schema_name):
        key_name = klass.key_from_names(owner_name, schema_name)
        return klass.get_by_key_name(key_name)

    def as_hash(self):
        result = {
            'name': self.name,
            'data': [ data.as_hash() for data in self.data_set ]
        }
        return result




