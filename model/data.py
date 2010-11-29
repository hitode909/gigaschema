from google.appengine.ext import db
from model.schema import Schema
import re
import datetime
import logging

class Data(db.Model):
    schema = db.ReferenceProperty(Schema, required=True)
    created_on = db.DateTimeProperty(auto_now=True)
    group = db.StringProperty()
    value = db.TextProperty()
    item_type = db.TextProperty()

    @classmethod
    def create(klass, schema=None, group=None, value=None):
        data = klass(
            schema=schema,
            group=group,
            value=value,
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
            )
            data.put()
            data.set_item_type()
            results.append(data)
            now = now.replace(microsecond = now.microsecond+1)
        return results

    def url(self):
        return self.schema.url() + '/' + str(self.key())

    def json_url(self):
        return self.url() + '.json'

    def as_hash(self):
        return {
            'timestamp': str(self.created_on),
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
        if not self.item_type:     # XXX
            logging.warn("fill in item_type")
            self.set_item_type()   # XXX

        return self.item_type == 'text'

    def is_number_item(self):
        return self.item_type == 'number'

    def is_image_item(self):
        return self.item_type == 'image'

    def is_audio_item(self):
        return self.item_type == 'audio'

    def is_url_item(self):
        return self.item_type == 'url'

    @classmethod
    def validate_group(klass, value):
        if not value:
            return True

        if len(value) > 500:
            return False

        return re.compile('^[^./]+$').match(value)

    def slug(self):
        return self.schema.slug() + '/' + str(self.key())
