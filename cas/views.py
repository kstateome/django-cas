"""CAS login/logout replacement views"""

from urllib import urlencode
from urlparse import urljoin

from django.http import get_host, HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib import messages
from cas import defaults as cas_defaults

__all__ = ['login', 'logout']

def _service_url(request, redirect_to=None):
    """Generates application service URL for CAS"""

    protocol = ('http://', 'https://')[request.is_secure()]
    if getattr(settings, 'CAS_IGNORE_HOST', cas_defaults.CAS_IGNORE_HOST):
        host = settings.CAS_ACTUAL_HOST
    else:
        host = get_host(request)
    service = protocol + host + request.path
    if redirect_to:
        if '?' in service:
            service += '&'
        else:
            service += '?'
        service += urlencode({REDIRECT_FIELD_NAME: redirect_to})
    return service


def _redirect_url(request):
    """Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.
    """

    next = request.GET.get(REDIRECT_FIELD_NAME)
    if not next:
        if settings.CAS_IGNORE_REFERER:
            next = settings.CAS_REDIRECT_URL
        else:
            next = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)
        if getattr(settings, 'CAS_IGNORE_HOST', cas_defaults.CAS_IGNORE_HOST):
            host = settings.CAS_ACTUAL_HOST
        else:
            host = get_host(request)
        prefix = (('http://', 'https://')[request.is_secure()] + host)
        if next.startswith(prefix):
            next = next[len(prefix):]
    return next


def _login_url(service):
    """Generates CAS login URL"""

    params = {'service': service}
    if settings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(settings.CAS_EXTRA_LOGIN_PARAMS)
    return urljoin(settings.CAS_SERVER_URL, 'login') + '?' + urlencode(params)


def _logout_url(request, next_page=None):
    """Generates CAS logout URL"""

    url = urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        protocol = ('http://', 'https://')[request.is_secure()]
        if getattr(settings, 'CAS_IGNORE_HOST', cas_defaults.CAS_IGNORE_HOST):
            host = settings.CAS_ACTUAL_HOST
        else:
            host = get_host(request)
        url += '?' + urlencode({'url': protocol + host + next_page})
    return url


def login(request, next_page=None, required=False):
    """Forwards to CAS login URL or verifies CAS ticket"""

    if not next_page:
        next_page = _redirect_url(request)
    if request.user.is_authenticated():
        message = "You are logged in as %s." % request.user.username
        messages.success(request, message)
        return HttpResponseRedirect(next_page)
    ticket = request.GET.get('ticket')
    service = _service_url(request, next_page)
    if ticket:
        from django.contrib import auth
        user = auth.authenticate(ticket=ticket, service=service)
        if user is not None:
            auth.login(request, user)
            name = user.first_name or user.username
            message = "Login succeeded. Welcome, %s." % name
            messages.success(request, message)
            return HttpResponseRedirect(next_page)
        elif settings.CAS_RETRY_LOGIN or required:
            return HttpResponseRedirect(_login_url(service))
        else:
            error = "<h1>Forbidden</h1><p>Login failed.</p>"
            return HttpResponseForbidden(error)
    else:
        return HttpResponseRedirect(_login_url(service))


def logout(request, next_page=None):
    """Redirects to CAS logout page"""

    from django.contrib.auth import logout
    logout(request)
    if not next_page:
        next_page = _redirect_url(request)
    if settings.CAS_LOGOUT_COMPLETELY:
        return HttpResponseRedirect(_logout_url(request, next_page))
    else:
        return HttpResponseRedirect(next_page)
