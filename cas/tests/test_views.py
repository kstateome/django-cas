from django.test import TestCase, RequestFactory
from django.test.utils import override_settings

from cas.views import _redirect_url, _login_url, _logout_url, _service_url


class RequestFactoryRemix(RequestFactory):

    path = '/'

    def get_host(self):
        return 'signin.k-state.edu'

    def is_secure(self):
        return False


class SecureRequestFactory(RequestFactory):

    path = '/'

    def get_host(self):
        return 'signin.k-state.edu'

    def is_secure(self):
        return True


class CASViewsTestCase(TestCase):

    def setUp(self):
        self.request = RequestFactoryRemix()
        self.request.GET = {}
        self.request.META = {}

    def test_service_url(self):
        self.assertEqual(_service_url(self.request), 'http://signin.k-state.edu/')

    @override_settings(CAS_FORCE_SSL_SERVICE_URL=True)
    def test_service_url_forced_ssl(self):
        self.assertEqual(_service_url(self.request), 'https://signin.k-state.edu/')

    def test_redirect_url(self):
        self.assertEqual(_redirect_url(self.request), '/')

        self.request.META = {'HTTP_REFERER': '/home/'}
        self.assertEqual(_redirect_url(self.request), '/home/')

        self.request.GET = {'next': 'foo'}
        self.assertEqual(_redirect_url(self.request), 'foo')

    @override_settings(CAS_IGNORE_REFERER=False)
    @override_settings(CAS_REDIRECT_URL=None)
    def test_https_redirect_url(self):
        self.request = SecureRequestFactory()
        self.request.GET = {}
        self.request.META = {'HTTP_REFERER': 'https://example.com/'}
        self.assertEqual(_redirect_url(self.request), 'https://example.com/')

    def test_login_url(self):
        self.assertEqual(_login_url('http://localhost:8000/accounts/login/'),
                         'http://signin.cas.com/login?service=http%3A%2F%2Flocalhost%3A8000%2Faccounts%2Flogin%2F')

    def test_logout_url(self):
        self.assertEqual(_logout_url(self.request), 'http://signin.cas.com/logout')
