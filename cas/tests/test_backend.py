import mock
from django.test import TestCase

from cas.backends import CASBackend
from cas.tests import factories


class CASBackendTest(TestCase):

    def setUp(self):
        self.user = factories.UserFactory.create()

    def test_get_user(self):
        backend = CASBackend()

        self.assertEqual(backend.get_user(self.user.pk), self.user)

    @mock.patch('cas.backends._verify')
    def test_user_auto_create(self, verify):
        username = 'faker'
        verify.return_value = username
        backend = CASBackend()

        with self.settings(CAS_AUTO_CREATE_USER=False):
            user = backend.authenticate('fake', 'fake')
            self.assertIsNone(user)

        with self.settings(CAS_AUTO_CREATE_USER=True):
            user = backend.authenticate('fake', 'fake')
            self.assertEquals(user.username, username)
