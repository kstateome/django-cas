import logging
import datetime

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from operator import itemgetter

from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib import auth
from django.core.urlresolvers import reverse

from cas.models import PgtIOU

__all__ = ['login', 'logout']

logger = logging.getLogger(__name__)


def _service_url(request, redirect_to=None, gateway=False):
    """
    Generates application service URL for CAS

    :param: request Request Object
    :param: redirect_to URL to redriect to
    :param: gateway Should this be a gatewayed pass through

    """

    if settings.CAS_FORCE_SSL_SERVICE_URL:
        protocol = 'https://'
    else:
        protocol = ('http://', 'https://')[request.is_secure()]
    host = request.get_host()
    service = protocol + host + request.path
    if redirect_to:
        if '?' in service:
            service += '&'
        else:
            service += '?'

        if gateway:
            """ If gateway, capture params and reencode them before returning a url """
            gateway_params = [(REDIRECT_FIELD_NAME, redirect_to), ('gatewayed', 'true')]
            query_dict = request.GET.copy()

            try:
                del query_dict['ticket']
            except:
                pass
            query_list = query_dict.items()

            # remove duplicate params
            for item in query_list:
                for index, item2 in enumerate(gateway_params):
                    if item[0] == item2[0]:
                        gateway_params.pop(index)
            extra_params = gateway_params + query_list

            #Sort params by key name so they are always in the same order.
            sorted_params = sorted(extra_params, key=itemgetter(0))

            service += urlencode(sorted_params)
        else:
            service += urlencode({REDIRECT_FIELD_NAME: redirect_to})

    return service


def _redirect_url(request):
    """
    Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.

    :param: request RequestObj

    """

    next = request.GET.get(REDIRECT_FIELD_NAME)

    if not next:
        if settings.CAS_IGNORE_REFERER:
            next = settings.CAS_REDIRECT_URL
        else:
            next = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)

        host = request.get_host()
        prefix = (('http://', 'https://')[request.is_secure()] + host)

        if next.startswith(prefix):
            next = next[len(prefix):]

    return next


def _login_url(service, ticket='ST', gateway=False):
    """
    Generates CAS login URL

    :param: service Service URL
    :param: ticket Ticket
    :param: gateway Gatewayed

    """

    LOGINS = {'ST': 'login',
              'PT': 'proxyValidate'}
    if gateway:
        params = {'service': service, 'gateway': 'true'}
    else:
        params = {'service': service}

    if settings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(settings.CAS_EXTRA_LOGIN_PARAMS)

    if not ticket:
        ticket = 'ST'

    login_type = LOGINS.get(ticket[:2], 'login')

    return urlparse.urljoin(settings.CAS_SERVER_URL, login_type) + '?' + urlencode(params)


def _logout_url(request, next_page=None):
    """
    Generates CAS logout URL

    :param: request RequestObj
    :param: next_page Page to redirect after logout.

    """

    url = urlparse.urljoin(settings.CAS_SERVER_URL, 'logout')

    if next_page and getattr(settings, 'CAS_PROVIDE_URL_TO_LOGOUT', True):
        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        url += '?' + urlencode({'url': protocol + host + next_page})

    return url


def login(request, next_page=None, required=False, gateway=False):
    """
    Forwards to CAS login URL or verifies CAS ticket

    :param: request RequestObj
    :param: next_page Next page to redirect after login
    :param: required
    :param: gateway Gatewayed response

    """

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
        user = auth.authenticate(ticket=ticket, service=service)

        if user is not None:

            auth.login(request, user)

            if settings.CAS_PROXY_CALLBACK:
                proxy_callback(request)

            return HttpResponseRedirect(next_page)
        elif settings.CAS_RETRY_LOGIN or required:
            if gateway:
                return HttpResponseRedirect(_login_url(service, ticket, True))
            else:
                return HttpResponseRedirect(_login_url(service, ticket, False))
        else:
            logger.warning('User has a valid ticket but not a valid session')
            # Has ticket, not session

            if gateway:
                # Gatewayed responses should nto redirect.
                return False

            if getattr(settings, 'CAS_CUSTOM_FORBIDDEN'):
                return HttpResponseRedirect(reverse(settings.CAS_CUSTOM_FORBIDDEN) + "?" + request.META['QUERY_STRING'])
            else:
                error = "<h1>Forbidden</h1><p>Login failed.</p>"
                return HttpResponseForbidden(error)
    else:
        if gateway:
            return HttpResponseRedirect(_login_url(service, ticket, True))
        else:
            return HttpResponseRedirect(_login_url(service, ticket, False))


def logout(request, next_page=None):
    """
    Redirects to CAS logout page

    :param: request RequestObj
    :param: next_page Page to redirect to

    """

    auth.logout(request)

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
        logger.info('No pgtIou or tgt found in request.GET')
        return HttpResponse('No pgtIOO', content_type="text/plain")

    try:
        PgtIOU.objects.create(tgt=tgt, pgtIou=pgtIou, created=datetime.datetime.now())
        request.session['pgt-TICKET'] = pgtIou
        return HttpResponse('PGT ticket is: {ticket}'.format(ticket=pgtIou), content_type="text/plain")
    except Exception as e:
        logger.warning('PGT storage failed. {message}'.format(
            message=e
        ))
        return HttpResponse('PGT storage failed for {request}'.format(request=str(request.GET)),
                            content_type="text/plain")

