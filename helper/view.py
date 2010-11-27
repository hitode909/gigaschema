import os
import logging
from google.appengine.ext.webapp import template

class ViewHelper:
    @classmethod
    def process(klass, template_name, template_values):
        path = os.path.join(os.path.dirname(__file__), '..', 'template', template_name + '.html')
        logging.info("process " + path)
        result = template.render(path, template_values)
        return result

