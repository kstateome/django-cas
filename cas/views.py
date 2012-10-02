"""CAS login/logout replacement views"""
from datetime import datetime
from urllib import urlencode
import urlparse

from django.http import get_host, HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from cas.models import PgtIOU
from django.contrib import messages

__all__ = ['login', 'logout']

def _service_url(request, redirect_to=None, gateway=False):
    """Generates application service URL for CAS"""

    protocol = ('http://', 'https://')[request.is_secure()]
    if settings.CAS_IGNORE_HOST:
        host = settings.CAS_ACTUAL_HOST
    else:
        host = get_host(request)
    prefix = (('http://', 'https://')[request.is_secure()] + host)
    service = protocol + host + request.path
    if redirect_to:        
        if '?' in service:
            service += '&'
        else:
            service += '?'
        if gateway:
            """ If gateway, capture params and reencode them before returning a url """
            split = redirect_to.split('?')
            redirect_to = split[0]
            parsed = urlparse.parse_qs(split[1])
            for k, v in parsed.iteritems():
                if len(v) == 1:
                    parsed[k] = v[0] #because parse_qs returns a list of params
        
            gateway_params = {REDIRECT_FIELD_NAME: redirect_to, 'gatewayed': 'true'}
            extra_params = dict(gateway_params.items() + parsed.items())
            service += urlencode(extra_params)
        else:
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
        if settings.CAS_IGNORE_HOST:
            host = settings.CAS_ACTUAL_HOST
        else:
            host = get_host(request)
        prefix = (('http://', 'https://')[request.is_secure()] + host)
        if next.startswith(prefix):
            next = next[len(prefix):]
    return next


def _login_url(service, ticket='ST', gateway=False):
    """Generates CAS login URL"""
    LOGINS = {'ST':'login',
              'PT':'proxyValidate'}
    if gateway:
        params = {'service': service, 'gateway':True}
    else:
        params = {'service': service}
    if settings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(settings.CAS_EXTRA_LOGIN_PARAMS)
    if not ticket:
        ticket = 'ST'
    login = LOGINS.get(ticket[:2],'login')
    return urlparse.urljoin(settings.CAS_SERVER_URL, login) + '?' + urlencode(params)


def _logout_url(request, next_page=None):
    """Generates CAS logout URL"""

    url = urlparse.urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        protocol = ('http://', 'https://')[request.is_secure()]
        if settings.CAS_IGNORE_HOST:
            host = settings.CAS_ACTUAL_HOST
        else:
            host = get_host(request)
        url += '?' + urlencode({'url': protocol + host + next_page})
    return url


def login(request, next_page=None, required=False, gateway=False):
    """Forwards to CAS login URL or verifies CAS ticket"""

    if not next_page:
        next_page = _redirect_url(request)
    if request.user.is_authenticated():
        return HttpResponseRedirect(next_page)
    ticket = request.GET.get('ticket')

    if gateway:
        service = _service_url(request, next_page, True)
    else:
        service = _service_url(request, next_page, False)
    if ticket:
        from django.contrib import auth
        user = auth.authenticate(ticket=ticket, service=service)

        if user is not None:
            auth.login(request, user)
            proxy_callback(request)
            return HttpResponseRedirect(next_page)
        elif settings.CAS_RETRY_LOGIN or required:
            if gateway:
                return HttpResponseRedirect(_login_url(service, ticket, True))
            else:
                return HttpResponseRedirect(_login_url(service, ticket, False))
        else:
            error = "<h1>Forbidden</h1><p>Login failed.</p>"
            return HttpResponseForbidden(error)
    else:
        if gateway:
            return HttpResponseRedirect(_login_url(service, ticket, True))
        else:
            return HttpResponseRedirect(_login_url(service, ticket, False))


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

def proxy_callback(request):
    """Handles CAS 2.0+ XML-based proxy callback call.
    Stores the proxy granting ticket in the database for 
    future use.
    
    NB: Use created and set it in python in case database
    has issues with setting up the default timestamp value
    """
    pgtIou = request.GET.get('pgtIou')
    tgt = request.GET.get('pgtId')

    if not (pgtIou and tgt):
        return HttpResponse('No pgtIOO', mimetype="text/plain")
    try:
        PgtIOU.objects.create(tgt = tgt, pgtIou = pgtIou, created = datetime.now())
        request.session['pgt-TICKET'] = ticket
        return HttpResponse('PGT ticket is: %s' % str(ticket, mimetype="text/plain"))
    except:
        return HttpResponse('PGT storage failed for %s' % str(request.GET), mimetype="text/plain")

    return HttpResponse('Success', mimetype="text/plain")

