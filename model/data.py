from google.appengine.ext import db
from model.schema import Schema
import base64
from google.appengine.api import memcache
import re
import datetime
import logging
from django.utils import simplejson
from helper import *

class Data(db.Model):
    schema = db.ReferenceProperty(Schema, required=True)
    created_on = db.DateTimeProperty(auto_now=True)
    group = db.StringProperty()
    value = db.TextProperty()
    item_type = db.TextProperty()
    owner = db.UserProperty(required=True)

    @classmethod
    def retrieve(klass, owner_name, schema_name, data_key, use_cache=False):
        key = '/'.join([owner_name,schema_name,data_key])
        data = None

        if use_cache:
            json = memcache.get(key=key)
            logging.info(key)
            logging.info(json)
            if (json) :
                data_hash = simplejson.loads(json);
                schema = Schema.retrieve(owner_name = owner_name, schema_name = schema_name, use_cache=True)
                datestr = re.sub(r'\.\d*$', '',  data_hash['created_on'])
                created_on = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
                group = data_hash['group']
                value = data_hash['value']
                item_type = data_hash['item_type']
                owner = schema.owner
                data = Data(
                    key = data_key,
                    schema = schema,
                    created_on = created_on,
                    group = group,
                    value = value,
                    item_type = item_type,
                    owner = schema.owner
                )
                logging.info('cach hit(data): ' + key)
        if not data:
            data = Data.get(data_key)
            if data:
                json = simplejson.dumps(data.as_dumpable_hash())
                memcache.set(key=key, value=json, time=60*60*24*10)

        return data

    def retrieve_all(klass):
        pass

    @classmethod
    def create(klass, schema=None, group=None, value=None):
        data = klass(
            schema=schema,
            group=group,
            value=value,
            owner=schema.owner,
        )
        data.put()
        data.set_item_type()
        return data

    @classmethod
    def create_multi(klass, schema=None, group=None, values=[]):
        if len(values) == 0:
            return

        now = datetime.datetime.now()

        results = []
        for value in values:
            data = klass(
                schema = schema,
                group = group,
                value = value,
                created_on = now,
                owner=schema.owner,
            )
            data.put()
            data.set_item_type()
            results.append(data)
            now = now.replace(microsecond = now.microsecond+1)
        return results

    def url(self):
        return self.schema.url() + '/' + str(self.key())

    def small_avatar_url(self):
        user = self.owner
        UserHelper.inject_params(user)
        return user.small_avatar_url

    def avatar_url(self):
        user = self.owner
        UserHelper.inject_params(user)
        return user.avatar_url

    def schema_name(self):
        return self.schema.name

    def json_url(self):
        return self.url() + '.json'

    def value_url(self):
        return self.url() + '.value'

    def as_hash(self):
        return {
            'created_on': str(self.created_on),
            'group': self.group,
            'value': self.output_value(),
            'item_type': self.item_type,
        }

    def as_dumpable_hash(self):
        return {
            'created_on': str(self.created_on),
            'group': self.group,
            'value': self.value,
            'item_type': self.item_type,
        }
    def set_item_type(self):
        if self.item_type:
            return

        self.item_type = self.get_item_type()
        self.put()

    def get_item_type(self):
        value = self.value

        r_url = re.compile('^(https?)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)$')
        r_url_img = re.compile('jpg|png|gif|bmp$', re.IGNORECASE)
        r_url_audio = re.compile('wav|mp3|m4a$', re.IGNORECASE)
        r_img = re.compile('^data:image/', re.IGNORECASE)
        r_audio = re.compile('^data:audio/', re.IGNORECASE)

        if r_img.match(value):
            return 'image'
        if r_audio.match(value):
            return 'audio'

        if r_url.match(value):
            if r_url_img.search(value):
                return 'image'
            if r_url_audio.search(value):
                return 'audio'
            return 'url'

        try:
            float(value)
            return 'number'
        except ValueError:
            return 'text'

    def is_text_item(self):
        return self.item_type == 'text'

    def is_number_item(self):
        return self.item_type == 'number'

    def is_image_item(self):
        return self.item_type == 'image'

    def is_audio_item(self):
        return self.item_type == 'audio'

    def is_url_item(self):
        return self.item_type == 'url'

    def output_value(self):
        if self.media_url():
            return self.media_url()
        else:
            return self.value

    @classmethod
    def validate_group(klass, value):
        if not value:
            return True

        if len(value) > 500:
            return False

        return re.compile('^[^./]+$').match(value)

    def slug(self):
        return self.schema.slug() + '/' + str(self.key())

    def media_url(self):
        blob_info = self.blob_info()
        if blob_info:
            return self.url() + '.' + blob_info['extname']

        return None

    def blob_info(self):
        if getattr(self, 'blob_info_cache', 'undef') != 'undef':
            return getattr(self, 'blob_info_cache')

        r = re.compile('^data:(.+)/(.+);base64,(.*)$', re.S)
        matched = r.match(self.value)
        if matched:
            b64 = matched.group(3)
            blob = base64.standard_b64decode(b64)
            self.blob_info_cache = {
                'blob': blob,
                'content-type': matched.group(1) + '/' + matched.group(2),
                'extname': matched.group(2)
                }
        else:
            self.blob_info_cache = None

        return self.blob_info_cache

