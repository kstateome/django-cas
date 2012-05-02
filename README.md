django-cas
==========

K-State&#39;s maintained version of django-cas

This is a fork of the original which lives here https://bitbucket.org/cpcc/django-cas/overview

Install
-------

See the document at Bitbucket

https://bitbucket.org/cpcc/django-cas/overview

Settings.py for CAS
-------------------

Add the following to middleware if you want to use CAS::
    
    MIDDLEWARE_CLASSES = (
    'cas.middleware.CASMiddleware',
    )
    

Add these to ``settings.py`` to use the CAS Backend::


    CAS_SERVER_URL = "Your Cas Server"
    CAS_LOGOUT_COMPLETELY = True


CAS on Poxies
-------------

Part of our reason for maintaining this fork is the ability to use CAS through proxies that do not 
send the proper HOST_HEADERS.  You can enable this by setting the following in your django settings file.

    CAS_ACTUAL_HOST = "" # This is set to your host, which is almost always k-state.edu
    CAS_IGNORE_HOST = False # Set this to true to enable ignoring of the host.

