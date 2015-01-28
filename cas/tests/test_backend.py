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