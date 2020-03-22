try:
    from unittest import mock
except ImportError:
    import mock

from urllib.parse import quote_plus, urlencode

from django.conf import settings
from django.test import TestCase, Client, override_settings, modify_settings



@override_settings(MIDDLEWARE=[
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cas.middleware.CASMiddleware'
])
class CASBackendTest(TestCase):

    def setUp(self):
        from cas.tests import factories
        self.user = factories.UserFactory.create()
        self.client = Client()

    def test_login_calls_cas_login(self):
        resp = self.client.get('/login/')
        self.assertTrue(resp.has_header('Location'))
        expected_url = '{}/login?{}'.format(
            settings.CAS_SERVER_URL,
            urlencode({
                'service': 'http://testserver/login/?next={}'.format(quote_plus('/'))
            })
        )
        self.assertRedirects(resp, expected_url, fetch_redirect_response=False)

    def test_logout_calls_cas_logout(self):
        resp = self.client.get('/logout/')
        self.assertTrue(resp.has_header('Location'))
        expected_url = '{}/logout?{}'.format(
            settings.CAS_SERVER_URL,
            urlencode({
                'service': 'http://testserver/'
            })
        )
        self.assertRedirects(resp, expected_url, fetch_redirect_response=False)