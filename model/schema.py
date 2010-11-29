from google.appengine.api import users
from google.appengine.ext import db
from time import time
from helper import *
import hashlib
import urllib
import re

class Schema(db.Model):
    name = db.StringProperty(required=True)
    origin = db.StringProperty()
    api_key = db.StringProperty()
    owner = db.UserProperty(required=True)
    created_on = db.DateTimeProperty(auto_now_add = True)

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

    def data(self, group=None, limit=50, offset=0, newer_first=True):
        q = Data.all()
        q.filter('schema = ', self.key())
        if group:
            q.filter('group = ', group)
        if newer_first:
            q.order('-created_on')
        else:
            q.order('created_on')

        data = q.fetch(limit, offset=offset)
        return data

    def data_at_page(self, group=None, page=1, per_page=100, newer_first=True):
        limit = per_page
        offset = (page-1) * per_page
        data = self.data(
            group = group,
            limit = limit + 1,
            offset = offset,
            newer_first = newer_first,
        )

        return {
            'data': data[0:limit+1],
            'page': page,
            'has_next': len(data) > limit,
            'next_page': page + 1,
            'has_prev': page > 1,
            'prev_page': page - 1,
        }

    def data_has_number(self):
        for item in self.data():
            if item.is_number_item():
                return True
        return False

    def url(self):
        return "/" + UserHelper.extract_user_name(self.owner) + "/" + urllib.quote(self.name.encode("utf-8"))

    def setting_url(self):
        return self.url() + ".setting"

    def json_url(self):
        return self.url() + ".json"

    def slug(self):
        return UserHelper.extract_user_name(self.owner) + "/" + self.name

    def as_hash(self, group=None, page=1, per_page=20):
        paged = self.data_at_page(page=page, per_page=per_page, group=group)

        has_prev = 1  if page > 1 else 0 
        result = {
            'name': self.name,
            'data': [ data.as_hash() for data in paged['data'] ],
            'has_next': paged['has_next'],
            'has_prev': has_prev,
            'page': paged['page'],
        }
        return result

    def as_hash_with_data(self, data=data):
        result = {
            'name': self.name,
            'data': [ d.as_hash() for d in data ],
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

    def current_user_can_delete(self, user = None):
        return self.current_user_can_post(user=user)

    def validate_value(self, value):
        return len(value) < 1000 * 1000 * 1000

    @classmethod
    def validate_name(klass, value):
        if len(value) > 500:
            return False

        return re.compile('^[^./]+$').match(value)

    @classmethod
    def validate_origin(klass, value):
        r_url = re.compile('^(https?)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)$')
        r_all = re.compile('^\\*$')

        if len(value) == 0:
            return True

        if len(value) > 500:
            return False

        if r_all.match(value):
            return True

        if r_url.match(value):
            return True

        return False

    def has_data(self):
        return len(self.data()) > 0

from model.data import Data
