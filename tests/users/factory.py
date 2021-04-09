"""Users factory"""

import factory
from rest_framework.authtoken.models import Token

from apps.users.models import User
from tests.utils import TEST_PASSWORD


class UserFactory(factory.django.DjangoModelFactory):
    """User factory"""

    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = User.Type.USER
    identification_type = User.IdentificationType.CC
    identification_number = factory.Faker('bothify', text='########')
    username = factory.LazyAttribute(lambda a: f"{a.first_name}{a.last_name}".lower())
    email = factory.LazyAttribute(lambda a: f'{a.first_name}.{a.last_name}@gmail.com'.lower())
    phone = factory.Faker('bothify', text='3#########')
    city = factory.Faker('city')
    neighborhood = factory.Faker('street_name')
    address = factory.Faker('street_address')
    password = factory.PostGenerationMethodCall('set_password', TEST_PASSWORD)


class UserDoctorFactory(UserFactory):
    """User doctor factory"""

    role = User.Type.DOCTOR
    city = 'Tunja'
    address = factory.Faker('address')


class UserAdminFactory(UserFactory):
    """User admin factory"""

    role = User.Type.ADMIN
    is_superuser = True
    is_staff = True
    city = 'Bogotá'
    address = factory.Faker('address')


class TokenFactory(factory.django.DjangoModelFactory):
    """Token factory"""

    class Meta:
        model = Token

    user = factory.SubFactory(UserFactory)
