from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from handler import *

def main():
    application = webapp.WSGIApplication(
        [
            ('/', IndexHandler),
            ('/([^./]+)/?', UserHandler),
            ('/([^./]+)/([^./]+).setting', SchemaSettingHandler),
            ('/([^./]+)/([^./]+).json', SchemaJsonHandler),
            ('/([^./]+)/([^./]+)/?', SchemaHandler),
            ('/([^./]+)/([^./]+)/([^./]+).json', DataJsonHandler),
            ('/([^./]+)/([^./]+)/([^./]+)/?', DataHandler),
            ],
        debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
        main()

