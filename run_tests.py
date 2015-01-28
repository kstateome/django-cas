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
                                       'cas',))
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
                       USE_TZ=True)


try:
    # Django 1.7 needs this, but other versions dont.
    django.setup()
except AttributeError:
    pass

from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=1)
failures = test_runner.run_tests(['cas', ])
if failures:
    sys.exit(failures)