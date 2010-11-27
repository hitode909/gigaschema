from google.appengine.ext import db

class Schema(db.Model):
    name = db.StringProperty(required=True)
    origin = db.StringProperty()
    rule = db.StringProperty()
    api_key = db.StringProperty()
    owner = db.UserProperty(required=True)
