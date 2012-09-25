# django-cas

K-State&#39;s maintained version of django-cas

This is a fork of the original which lives here https://bitbucket.org/cpcc/django-cas/overview

## Install


See the document at Bitbucket

https://bitbucket.org/cpcc/django-cas/overview

## Settings.py for CAS

Add the following to middleware if you want to use CAS::
    
    MIDDLEWARE_CLASSES = (
    'cas.middleware.CASMiddleware',
    )
    

Add these to ``settings.py`` to use the CAS Backend::


    CAS_SERVER_URL = "Your Cas Server"
    CAS_LOGOUT_COMPLETELY = True

# Additional Features

This fork contains additional features not found in the original:
*  Proxied Hosts
*  CAS Response Callbacks
*  CAS Gateway
*  Proxy Tickets (From Edmund Crewe) 

## Proxied Hosts

You will need to setup middleware to handle the use of proxies.


## CAS Response Callbacks

To store data from CAS, create a callback function that accepts the ElementTree object from the
proxyValidate response. There can be multiple callbacks, and they can live anywhere. Define the 
callback(s) in ``settings.py``:

    CAS_RESPONSE_CALLBACKS = (
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
        

## CAS Gateway

To use the CAS Gateway feature, first enable it in settings. Trying to use it without explicitly
enabling this setting will raise an ImproperlyConfigured:

    CAS_GATEWAY = True

Then, add the ``gateway`` decorator to a view:

    from cas.decorators import gateway

    @gateway()
    def foo(request):
        #stuff
        return render(request, 'foo/bar.html')

        
## Proxy Tickets

This fork also includes Edmund Crewe's proxy ticket patch:
http://code.google.com/r/edmundcrewe-proxypatch/source/browse/django-cas-proxy.patch