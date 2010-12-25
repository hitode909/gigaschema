import os
import logging
from google.appengine.ext.webapp import template
from django.utils import simplejson

def _template_path(template_name, template_type):
    return os.path.join(os.path.dirname(__file__), '..', 'template', template_name + '.' + template_type)

class ViewHelper:

    @classmethod
    def process(klass, template_name, template_values):
        path = _template_path(template_name, 'html')
        logging.info("process " + path)
        result = template.render(path, template_values)
        return result

    @classmethod
    def process_feed(klass, template_name, template_values):
        path = _template_path(template_name, 'feed')
        logging.info("process " + path)
        result = template.render(path, template_values)
        return result

    @classmethod
    def process_data(klass, data):
        return simplejson.dumps(data)



