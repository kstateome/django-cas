default_app_config = 'cas.apps.CASConfig'

from django.conf import settings

__all__ = []

_DEFAULTS = {
    'CAS_ADMIN_PREFIX': None,
    'CAS_EXTRA_LOGIN_PARAMS': None,
    'CAS_IGNORE_REFERER': False,
    'CAS_LOGOUT_COMPLETELY': True,
    'CAS_REDIRECT_URL': '/',
    'CAS_RETRY_LOGIN': False,
    'CAS_SERVER_URL': None,
    'CAS_VERSION': '2',
    'CAS_GATEWAY': False,
    'CAS_PROXY_CALLBACK': None,
    'CAS_RESPONSE_CALLBACKS': None,
    'CAS_CUSTOM_FORBIDDEN': None,
    'CAS_PGT_FETCH_WAIT': True,
    'CAS_FORCE_SSL_SERVICE_URL': False,
    'CAS_AUTO_CREATE_USER': True,
}

for key, value in _DEFAULTS.items():
    try:
        getattr(settings, key)
    except AttributeError:
        setattr(settings, key, value)
    # Suppress errors from DJANGO_SETTINGS_MODULE not being set
    except ImportError:
        pass
