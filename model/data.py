from google.appengine.ext import db
from model.schema import Schema
import re

class Data(db.Model):
    schema = db.ReferenceProperty(Schema, required=True)
    created_on = db.DateTimeProperty(auto_now=True)
    value = db.TextProperty()

    @classmethod
    def create(klass, schema=None, value=None):
        data = klass(
            schema=schema,
            value=value
        )
        data.put()
        return data

    def url(self):
        return self.schema.url() + '/' + str(self.key())

    def as_hash(self):
        return {
            'timestamp': str(self.created_on),
            'value': self.value,
        }


    def item_type(self):
        r_url = re.compile('^(https?)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)$')
        r_url_img = re.compile('jpg|png|gif|bmp$', re.IGNORECASE)
        r_url_audio = re.compile('wav|mp3|m4a$', re.IGNORECASE)
        r_img = re.compile('^data:image/', re.IGNORECASE)
        r_audio = re.compile('^data:audio/', re.IGNORECASE)

        if r_img.match(self.value):
            return 'image'
        if r_audio.match(self.value):
            return 'audio'

        if r_url.match(self.value):
            if r_url_img.search(self.value):
                return 'image'
            if r_url_audio.search(self.value):
                return 'audio'
            return 'url'

        try:
            float(self.value)
            return 'number'
        except ValueError:
            return 'text'

    def is_text_item(self):
        return self.item_type() == 'text'

    def is_number_item(self):
        return self.item_type() == 'number'

    def is_image_item(self):
        return self.item_type() == 'image'

    def is_audio_item(self):
        return self.item_type() == 'audio'

    def is_url_item(self):
        return self.item_type() == 'url'

