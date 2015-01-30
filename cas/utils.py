import logging

from django.conf import settings


logger = logging.getLogger(__name__)


def cas_response_callbacks(tree):
    callbacks = []
    callbacks.extend(settings.CAS_RESPONSE_CALLBACKS)

    for path in callbacks:
        i = path.rfind('.')
        module, callback = path[:i], path[i+1:]
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
