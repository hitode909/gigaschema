from google.appengine.ext import db
from model.schema import Schema

class Data(db.Model):
    schema = db.ReferenceProperty(Schema, required=True)
    datetime = db.DateTimeProperty(auto_now=True)
    value = db.StringProperty()