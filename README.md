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


Storing Data from CAS
-------------

To store data from CAS, create a callback function that accepts the ElementTree object from the
proxyValidate response. There can be multiple callbacks, and they can live anywhere. Define the 
callback(s) in ``settings.py``:

    CAS_RESPONSE_CALLBACK = (
        'path.to.module.callbackfunction',
        'anotherpath.to.module.callbackfunction2',
    )

and create the functions in ``path/to/module.py``:

    def callbackfunction(tree):
        username = tree[0][0].text

        user, user_created = User.objects.get_or_create(username=username)
        profile, created = user.get_profile()

        profile.email = tree[0][1].text
        profile.position = tree[0][2].text
        profile.save()
        

Using CAS Gateway Feature
-------------

To use the CAS Gateway feature, first enable it in settings. Trying to use it without explicitly
enabling this setting will raise an ImproperlyConfigured:

    CAS_GATEWAY = True

Then, add the ``gateway`` decorator to a view:

    from cas.decorators import gateway

    @gateway
    def foo(request):
        #stuff
        return render(request, 'foo/bar.html')