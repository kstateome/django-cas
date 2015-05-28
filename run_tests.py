#!/usr/bin/env python

import os, sys
from django.conf import settings
import django

DIRNAME = os.path.dirname(__file__)

if django.VERSION[1] < 4:
    # If the version is NOT django 4 or greater
    # then remove the TZ setting.

    settings.configure(DEBUG=True,
                       DATABASES={
                           'default': {
                               'ENGINE': 'django.db.backends.sqlite3',
                               }
                       },
                       #ROOT_URLCONF='mailqueue.urls',
                       INSTALLED_APPS=('django.contrib.auth',
                                       'django.contrib.contenttypes',
                                       'django.contrib.sessions',
                                       'django.contrib.admin',
                                       'cas',),
                       CAS_SERVER_URL = 'http://signin.cas.com',
                       )
else:
    settings.configure(DEBUG=True,
                       DATABASES={
                           'default': {
                               'ENGINE': 'django.db.backends.sqlite3',
                               }
                       },
                       #ROOT_URLCONF='mailqueue.urls',
                       INSTALLED_APPS=('django.contrib.auth',
                                       'django.contrib.contenttypes',
                                       'django.contrib.sessions',
                                       'django.contrib.admin',
                                       'cas',),
                       USE_TZ=True,
                       CAS_SERVER_URL = 'http://signin.cas.com',)


try:
    # Django 1.7 needs this, but other versions dont.
    django.setup()
except AttributeError:
    pass

try:
    from django.test.simple import DjangoTestSuiteRunner
    test_runner = DjangoTestSuiteRunner(verbosity=1)
except ImportError:
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
failures = test_runner.run_tests(['cas', ])
if failures:
    sys.exit(failures)
