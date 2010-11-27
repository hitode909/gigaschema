from google.appengine.ext import db

class Data(db.Model):
    schema = db.ReferenceProperty(Schema)
    datetime = db.DateTimeProperty(auto_now=True)
    value = db.StringProperty()
