try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.http import urlquote
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

__all__ = ['permission_required', 'user_passes_test']


def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Replacement for django.contrib.auth.decorators.user_passes_test that
    returns 403 Forbidden if the user is already logged in.
    """

    if not login_url:
        login_url = settings.LOGIN_URL

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            try:
                # use callable for pre-django 2.0
                is_authenticated = request.user.is_authenticated()
            except TypeError:
                is_authenticated = request.user.is_authenticated

            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            elif is_authenticated:
                return HttpResponseForbidden('<h1>Permission denied</h1>')
            else:
                path = '%s?%s=%s' % (login_url, redirect_field_name,
                                     urlquote(request.get_full_path()))
                return HttpResponseRedirect(path)
        return wrapper
    return decorator


def permission_required(perm, login_url=None):
    """
    Replacement for django.contrib.auth.decorators.permission_required that
    returns 403 Forbidden if the user is already logged in.
    """

    return user_passes_test(lambda u: u.has_perm(perm), login_url=login_url)


def gateway():
    """
    Authenticates single sign on session if ticket is available,
    but doesn't redirect to sign in url otherwise.
    """

    if settings.CAS_GATEWAY == False:
        raise ImproperlyConfigured('CAS_GATEWAY must be set to True')

    def wrap(func):
        def wrapped_f(*args):

            from cas.views import login
            request = args[0]

            try:
                # use callable for pre-django 2.0
                is_authenticated = request.user.is_authenticated()
            except TypeError:
                is_authenticated = request.user.is_authenticated

            if is_authenticated:
                # Is Authed, fine
                pass
            else:
                path_with_params = request.path + '?' + urlencode(request.GET.copy())
                if request.GET.get('ticket'):
                    # Not Authed, but have a ticket!
                    # Try to authenticate
                    response = login(request, path_with_params, False, True)
                    if isinstance(response, HttpResponseRedirect):
                        # For certain instances where a forbidden occurs, we need to pass instead of return a response.
                        return response
                else:
                    #Not Authed, but no ticket
                    gatewayed = request.GET.get('gatewayed')
                    if gatewayed == 'true':
                        pass
                    else:
                        # Not Authed, try to authenticate
                        response = login(request, path_with_params, False, True)
                        if isinstance(response, HttpResponseRedirect):
                            return response

            return func(*args)
        return wrapped_f
    return wrap
