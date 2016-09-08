from importlib import import_module
import logging

from django.conf import settings
import re
import six
import sys

logger = logging.getLogger(__name__)

EMAIL_REGX = re.compile(r'^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$')


def cas_response_callbacks(tree):
    callbacks = []
    callbacks.extend(settings.CAS_RESPONSE_CALLBACKS)

    for path in callbacks:
        i = path.rfind('.')
        module, callback = path[:i], path[i + 1:]
        try:
            mod = __import__(module, fromlist=[''])
        except ImportError as e:
            logger.error("Import Error: %s" % e)
            raise e
        try:
            func = getattr(mod, callback)
        except AttributeError as e:
            logger.error("Attribute Error: %s" % e)
            raise e
        func(tree)


def is_email(string):
    return EMAIL_REGX.match(string)


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
        module = import_module(module_path)

        try:
            return getattr(module, class_name)
        except AttributeError:
            msg = 'Module "%s" does not define a "%s" attribute/class' % (
                module_path, class_name)
            six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])
