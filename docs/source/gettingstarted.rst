Getting Started
===============

Requirements
------------

CAS client for Django.  This library requires Django 1.5 or above, and Python 2.6, 2.7, 3.4


Install
-------

This project is registered on PyPi as django-cas-client.  To install::

    pip install django-cas-client==1.1.1

Configuration
-------------

**Add to URLs**

Add the login and logout patterns to your main URLS conf::

    url(r'^accounts/login/$', 'cas.views.login', name='login'),
    url(r'^accounts/logout/$', 'cas.views.logout', name='logout'),

**Add middleware and settings**

Set your CAS server URL::

    CAS_SERVER_URL = "https://signin.somehwere/cas/"

Add cas to middleware classes::

    'cas.middleware.CASMiddleware',


**Add authentication backends**
::

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'cas.backends.CASBackend',
    )

**Settings**

Add the following to middleware if you want to use CAS::

    MIDDLEWARE_CLASSES = (
    'cas.middleware.CASMiddleware',
    )


Add these to ``settings.py`` to use the CAS Backend::


    CAS_SERVER_URL = "Your Cas Server"
    CAS_LOGOUT_COMPLETELY = True
    CAS_PROVIDE_URL_TO_LOGOUT = True

**Proxied Hosts**

You will need to setup middleware to handle the use of proxies.

Add a setting ``PROXY_DOMAIN`` of the domain you want the client to use.  Then add::

    MIDDLEWARE_CLASSES = (
    'cas.middleware.ProxyMiddleware',
    )

This middleware needs to be added before the django ``common`` middleware.


**CAS Response Callbacks**

To store data from CAS, create a callback function that accepts the ElementTree object from the
proxyValidate response. There can be multiple callbacks, and they can live anywhere. Define the
callback(s) in ``settings.py``::

    CAS_RESPONSE_CALLBACKS = (
        'path.to.module.callbackfunction',
        'anotherpath.to.module.callbackfunction2',
    )

and create the functions in ``path/to/module.py``::

    def callbackfunction(tree):
        username = tree[0][0].text

        user, user_created = User.objects.get_or_create(username=username)
        profile, created = user.get_profile()

        profile.email = tree[0][1].text
        profile.position = tree[0][2].text
        profile.save()


**CAS Gateway**

To use the CAS Gateway feature, first enable it in settings. Trying to use it without explicitly
enabling this setting will raise an ImproperlyConfigured::

    CAS_GATEWAY = True

Then, add the ``gateway`` decorator to a view::

    from cas.decorators import gateway

    @gateway()
    def foo(request):
        return render(request, 'foo/bar.html')


**Custom Forbidden Page**

To show a custom forbidden page, set ``CAS_CUSTOM_FORBIDDEN`` to a ``path.to.some_view``.  Otherwise,
a generic ``HttpResponseForbidden`` will be returned.

**Require SSL Login**

To force the service url to always target HTTPS, set ``CAS_FORCE_SSL_SERVICE_URL`` to ``True``.

**Automatically Create Users on First Login**

By default, a stub user record will be created on the first successful CAS authentication
using the username in the response. If this behavior is not desired set
``CAS_AUTO_CREATE_USER`` to ``Flase``.

**Proxy Tickets**

This fork also includes
[Edmund Crewe's proxy ticket patch](http://code.google.com/r/edmundcrewe-proxypatch/source/browse/django-cas-proxy.patch).
