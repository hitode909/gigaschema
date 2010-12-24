from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from handler import *

def main():
    application = webapp.WSGIApplication(
        [
            ('/', IndexHandler),
            ('/help/?', HelpHandler),
            ('/create/?', CreateHandler),
            ('/data/?', RecentDataHandler),
            ('/schema/?', RecentSchemaHandler),
            ('/user/?', UserRedirectHandler),
            ('/([^./]+)/?', UserHandler),
            ('/([^./]+)/([^./]+).setting', SchemaSettingHandler),
            ('/([^./]+)/([^./]+)/?.json', SchemaJsonHandler),
            ('/([^./]+)/([^./]+)/?', SchemaHandler),
            ('/([^./]+)/([^./]+)/([^./]+)/?.json', DataJsonHandler),
            ('/([^./]+)/([^./]+)/([^./]+)/?.value', DataValueHandler),
            ('/([^./]+)/([^./]+)/([^./]+)\.([^./]+)', DataMediaHandler),
            ('/([^./]+)/([^./]+)/([^./]+)/?', DataHandler),
            ],
        debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
        main()

