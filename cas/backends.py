"""CAS authentication backend"""

import logging
from urllib import urlencode, urlopen
from urlparse import urljoin
from xml.dom import minidom

from django.conf import settings
from django.contrib.auth import get_user_model
from cas.exceptions import CasTicketException
from cas.models import Tgt, PgtIOU
from cas.utils import cas_response_callbacks

__all__ = ['CASBackend']

logger = logging.getLogger(__name__)

def _verify_cas1(ticket, service):
    """Verifies CAS 1.0 authentication ticket.

    Returns username on success and None on failure.
    """

    params = {'ticket': ticket, 'service': service}
    url = (urljoin(settings.CAS_SERVER_URL, 'validate') + '?' +
           urlencode(params))
    page = urlopen(url)
    try:
        verified = page.readline().strip()
        if verified == 'yes':
            return page.readline().strip()
        else:
            return None
    finally:
        page.close()


def _verify_cas2(ticket, service):
    """Verifies CAS 2.0+ XML-based authentication ticket.

    Returns username on success and None on failure.
    """

    try:
        from xml.etree import ElementTree
    except ImportError:
        from elementtree import ElementTree

    params = {'ticket': ticket, 'service': service}
    if settings.CAS_PROXY_CALLBACK:
        params['pgtUrl'] = settings.CAS_PROXY_CALLBACK

    url = (urljoin(settings.CAS_SERVER_URL, 'proxyValidate') + '?' +
           urlencode(params))

    page = urlopen(url)

    username = None

    try:
        response = page.read()
        tree = ElementTree.fromstring(response)
        document = minidom.parseString(response)

        #Useful for debugging
        #print document.toprettyxml()

        if tree[0].tag.endswith('authenticationSuccess'):
            if settings.CAS_RESPONSE_CALLBACKS:
                cas_response_callbacks(tree)

            username = tree[0][0].text

            pgt_el = document.getElementsByTagName('cas:proxyGrantingTicket')
            if pgt_el:
                pgt = pgt_el[0].firstChild.nodeValue
                try:
                    pgtIou = _get_pgtiou(pgt)
                    tgt = Tgt.objects.get(username=username)
                    tgt.tgt = pgtIou.tgt
                    tgt.save()
                    pgtIou.delete()
                except Tgt.DoesNotExist:
                    Tgt.objects.create(username=username, tgt=pgtIou.tgt)
                    pgtIou.delete()
                except Exception:
                    logger.error('Failed to do proxy authentication.')

        else:
            failure = document.getElementsByTagName('cas:authenticationFailure')
            if failure:
                logger.warn('Authentication failed from CAS server: %s',
                            failure[0].firstChild.nodeValue)

    except Exception as e:
        logger.error('Failed to verify CAS authentication', e)

    finally:
        page.close()

    return username


def verify_proxy_ticket(ticket, service):
    """Verifies CAS 2.0+ XML-based proxy ticket.

    Returns username on success and None on failure.
    """

    try:
        from xml.etree import ElementTree
    except ImportError:
        from elementtree import ElementTree

    params = {'ticket': ticket, 'service': service}

    url = (urljoin(settings.CAS_SERVER_URL, 'proxyValidate') + '?' +
           urlencode(params))

    page = urlopen(url)

    try:
        response = page.read()
        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            username = tree[0][0].text
            proxies = []
            if len(tree[0]) > 1:
                for element in tree[0][1]:
                    proxies.append(element.text)
            return {"username": username, "proxies": proxies}
        else:
            return None
    finally:
        page.close()

_PROTOCOLS = {'1': _verify_cas1, '2': _verify_cas2}

if settings.CAS_VERSION not in _PROTOCOLS:
    raise ValueError('Unsupported CAS_VERSION %r' % settings.CAS_VERSION)

_verify = _PROTOCOLS[settings.CAS_VERSION]


def _get_pgtiou(pgt):
    """ Returns a PgtIOU object given a pgt.

        The PgtIOU (tgt) is set by the CAS server in a different request
        that has completed before this call, however, it may not be found in
        the database by this calling thread, hence the attempt to get the
        ticket is retried for up to 5 seconds. This should be handled some
        better way.
    """
    pgtIou = None
    retries_left = 5
    while not pgtIou and retries_left:
        try:
            return PgtIOU.objects.get(tgt=pgt)
        except PgtIOU.DoesNotExist:
            time.sleep(1)
            retries_left -= 1
    raise CasTicketException("Could not find pgtIou for pgt %s" % pgt)


class CASBackend(object):
    """CAS authentication backend"""

    supports_object_permissions = False
    supports_inactive_user = False

    def authenticate(self, ticket, service):
        """Verifies CAS ticket and gets or creates User object
            NB: Use of PT to identify proxy
        """
        User = get_user_model()
        username = _verify(ticket, service)
        if not username:
            return None
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            # user will have an "unusable" password
            user = User.objects.create_user(username, '')
            user.save()
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""

        User = get_user_model()
        
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
