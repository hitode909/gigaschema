from google.appengine.ext import db
from model.schema import Schema

class Data(db.Model):
    schema = db.ReferenceProperty(Schema, required=True)
    created_on = db.DateTimeProperty(auto_now=True)
    value = db.StringProperty()

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
