from django.test import TestCase, RequestFactory, override_settings
from django.test.utils import override_settings

from cas.views import _redirect_url, _login_url, _logout_url, _service_url


def custom_cas_server_url(service):
    if 'secret' in service:
        return 'http://secret.cas.com'
    return 'http://signin.cas.com/'


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


    @override_settings(CAS_SERVER_URL_CALLBACK='cas.tests.test_views.custom_cas_server_url')
    def test_login_url_custom(self):
        self.assertEqual(_login_url('http://localhost:8000/accounts/login/?return_url=/secret/'),
                         'http://secret.cas.com/login?service=http%3A%2F%2Flocalhost%3A8000%2Faccounts%2Flogin%2F%3Freturn_url%3D%2Fsecret%2F')

    @override_settings(CAS_SERVER_URL_CALLBACK='cas.tests.test_views.custom_cas_server_url')
    def test_login_url_custom_normal(self):
        self.assertEqual(_login_url('http://localhost:8000/accounts/login/?return_url=/normal/'),
                         'http://signin.cas.com/login?service=http%3A%2F%2Flocalhost%3A8000%2Faccounts%2Flogin%2F%3Freturn_url%3D%2Fnormal%2F')

    @override_settings(CAS_SERVER_URL_CALLBACK='cas.nonexistent.callback')
    def test_login_url_bad_callback_raises_exception(self):
        with self.assertRaises(RuntimeError):
            _ = _login_url('http://localhost:8000/accounts/login/?return_url=/normal/')
