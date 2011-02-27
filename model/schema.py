from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache
from django.utils import simplejson
from time import time
from helper import *
import hashlib
import urllib
import re
import datetime
import logging

class Schema(db.Model):
    name = db.StringProperty(required=True)
    origin = db.StringProperty()
    api_key = db.StringProperty()
    owner = db.UserProperty(required=True)
    created_on = db.DateTimeProperty(auto_now_add = True)
    updated_on = db.DateTimeProperty(auto_now = True)

    @classmethod
    def retrieve(klass, owner_name, schema_name, use_cache=False):
        key = klass.key_from_names(owner_name, schema_name)
        schema = None

        if use_cache :
            json = memcache.get(key=key)
            if (json) :
                schema_hash = simplejson.loads(json);
                name = schema_hash['name']
                origin = schema_hash['origin']
                api_key = schema_hash['api_key']
                owner = users.User(schema_hash['owner_mail'])
                datestr = re.sub(r'\.\d*$', '',  schema_hash['created_on'])
                created_on = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
                schema = Schema(
                    key_name = key,
                    name=name,
                    origin=origin,
                    api_key=api_key,
                    owner=owner,
                    created_on=created_on,
                )
                logging.info('cache hit(schema): ' + key)

        if not schema:
            schema = Schema.retrieve_by_names(owner_name, schema_name)
            if schema:
                json = simplejson.dumps(schema.as_dumpable_hash())
                memcache.set(key=key, value=json, time=60*60*24*10)

        return schema

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

    def delete_with_data(self):
        for data in self.data_set:
            data.delete()
        self.delete()

    def reset_api_key(self):
        s = hashlib.sha1()
        s.update(str(time()))
        s.update(self.name.encode('utf-8'))
        s.update(self.owner.user_id())
        self.api_key = s.hexdigest()
        self.put();

    def data_cache_all_key(self):
        return '/'.join([self.key().name(), 'data_cache_all'])

    def add_data_cache_all_key(self, addkey):
        key = self.data_cache_all_key()
        json = memcache.get(key)
        data_cache_key_dict = {}
        logging.info('adding cache...')
        if json:
            data_cache_key_dict = simplejson.loads(json)

        data_cache_key_dict[addkey] = 1
        logging.info(simplejson.dumps(data_cache_key_dict))

        memcache.set(key=key, value=simplejson.dumps(data_cache_key_dict), time=60*60*24*14)

    def clear_data_cache_all(self):
        logging.info('clearing..')
        key = self.data_cache_all_key()
        json = memcache.get(key)
        if json:
            data_cache_key_list = simplejson.loads(json)
            logging.info('clearing these: ' + json)
            memcache.delete_multi(data_cache_key_list.keys())

    def data(self, group=None, limit=50, offset=0, newer_first=True, use_cache=False):
        key = '/'.join([self.key().name(), 'data', str(group), str(limit), str(offset), str(newer_first)])
        data = []

        if use_cache :
            cache_enabled = memcache.get(key=self.data_cache_all_key())
            json = memcache.get(key=key)
            if (cache_enabled and json) :
                data_key_list = simplejson.loads(json);
                for data_key in data_key_list:
                    data.append(Data.retrieve(UserHelper.extract_user_name(self.owner), self.name, data_key, use_cache=True))
                logging.info('cache hit(schema_data): ' + key)

        if len(data) == 0:
            q = Data.all()
            q.filter('schema = ', self.key())
            q.filter('is_deleted =', False)
            if group:
                q.filter('group = ', group)
            if newer_first:
                q.order('-created_on')
            else:
                q.order('created_on')

            data = q.fetch(limit, offset=offset)

            data_key_list = []
            for d in data:
                data_key_list.append(str(d.key()))
            json = simplejson.dumps(data_key_list)
            memcache.set(key=key, value=json, time=60*60*24*10)
            self.add_data_cache_all_key(key)

        return data

    def data_at_page(self, group=None, page=1, per_page=100, newer_first=True, use_cache=False):
        limit = per_page
        offset = (page-1) * per_page
        data = self.data(
            group = group,
            limit = limit + 1,
            offset = offset,
            newer_first = newer_first,
            use_cache = use_cache
        )

        return {
            'data': data[0:limit],
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

    def feed_url(self):
        return self.url() + ".feed"

    def random_json_value_url(self):
        return self.url() + "/random.json"

    def slug(self):
        return UserHelper.extract_user_name(self.owner) + "/" + self.name

    def as_hash(self, group=None, page=1, per_page=20,use_cache=False):
        paged = self.data_at_page(page=page, per_page=per_page, group=group, use_cache=use_cache)

        result = {
            'name': self.name,
            'data': [ data.as_hash() for data in paged['data'] ],
            'has_next': paged['has_next'],
            'has_prev': page > 1,
            'page': paged['page'],
        }
        return result

    def as_hash_with_data(self, data=data):
        result = {
            'name': self.name,
            'data': [ d.as_hash() for d in data ],
        }
        return result

    def as_dumpable_hash(self) :
        name = db.StringProperty(required=True)
        origin = db.StringProperty()
        api_key = db.StringProperty()
        owner = db.UserProperty(required=True)
        created_on = db.DateTimeProperty(auto_now_add = True)
        result = {
            'name': self.name,
            'origin': self.origin,
            'api_key': self.api_key,
            'owner_mail': self.owner.email(),
            'created_on': str(self.created_on),
        }
        return result

    def current_user(self):
        return users.get_current_user()

    def current_user_is_owner(self):
        return self.owner == self.current_user()

    def current_user_can_post(self, user = None):
        if not user:
            user = self.current_user()
        if not self.api_key:
            return True

        return self.owner == user

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

    def small_avatar_url(self):
        user = self.owner
        UserHelper.inject_params(user)
        return user.small_avatar_url

    def avatar_url(self):
        user = self.owner
        UserHelper.inject_params(user)
        return user.avatar_url

    def updated_now(self):
        self.updated_on = datetime.datetime.today()
        self.put();

    def log(self):
        logging.info('log(schema): ' + str(self.key()))
        return ""

from model.data import Data
