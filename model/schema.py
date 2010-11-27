from google.appengine.ext import db
from time import time
import hashlib

class Schema(db.Model):
    name = db.StringProperty(required=True)
    origin = db.StringProperty()
    rule = db.StringProperty()
    api_key = db.StringProperty()
    owner = db.UserProperty(required=True)

    @classmethod
    def create_with_key(klass, **args):

        key_name = args['owner'].user_id() + '/' + args['name']

        api_key = None
        if args['with_api_key']:
            s = hashlib.sha1()
            s.update(str(time()))
            s.update(name.encode('utf-8'))
            s.update(args['user'].user_id())
            api_key = s.hexdigest()

        schema = klass(
            key_name=key_name,
            name=args['name'],
            origin=args['origin'],
            rule=args['rule'],
            owner=args['owner']
        );
        schema.put()

        return schema

