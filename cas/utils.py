import logging

from django.conf import settings
from django.utils.module_loading import import_string

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

def get_cas_server_url(service):
    try:
        cas_server_url_callback = settings.CAS_SERVER_URL_CALLBACK
    except AttributeError:
        pass
    else:
        try:
            callback = import_string(cas_server_url_callback)
        except ImportError:
            raise RuntimeError(
                "Invalid callback for CAS_SERVER_URL_CALLBACK: {}".format(
                    cas_server_url_callback
                )
            )
        return callback(service)
    return settings.CAS_SERVER_URL
