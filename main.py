from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from handler.index import IndexHandler
# from handler.schema import SchemaHandler
# from handler.data import DataHandler

def main():
    application = webapp.WSGIApplication(
        [
            ('/', IndexHandler),
            # ('/(\w+)/(\w+)', SchemaHandler),
            # ('/(\w+)/(\w+)/(\w+)', DataHandler),
            ],
        debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
        main()

