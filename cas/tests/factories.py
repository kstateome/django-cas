from django.contrib.auth.models import User


import factory


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = "derekst"
    first_name = "new"
    last_name = "user"
    is_staff = True
    password = factory.PostGenerationMethodCall('set_password', '1234')