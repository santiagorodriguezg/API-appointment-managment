"""Users factory"""

import factory
from rest_framework.authtoken.models import Token

from apps.accounts.models import User
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
    username = factory.LazyAttribute(lambda o: f"{o.first_name}{o.last_name}".lower())
    email = factory.Faker('free_email')
    phone = factory.Faker('bothify', text='3#########')
    city = factory.Faker('city')
    neighborhood = factory.Faker('street_name')
    address = factory.Faker('street_address')
    password = TEST_PASSWORD

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", None)
        obj = model_class(*args, **kwargs)
        obj.set_password(password)
        obj.save()
        return obj


class UserDoctorFactory(UserFactory):
    """User doctor factory"""

    role = User.Type.DOCTOR


class UserAdminFactory(UserFactory):
    """User admin factory"""

    role = User.Type.ADMIN
    is_superuser = True
    is_staff = True


class TokenFactory(factory.django.DjangoModelFactory):
    """Token factory"""

    class Meta:
        model = Token

    user = factory.SubFactory(UserFactory)


USER_FACTORY_DICT = factory.build(dict, FACTORY_CLASS=UserFactory)
USER_DOCTOR_FACTORY_DICT = factory.build(dict, FACTORY_CLASS=UserDoctorFactory)
USER_ADMIN_FACTORY_DICT = factory.build(dict, FACTORY_CLASS=UserAdminFactory)

USER_FACTORY_DICT.setdefault('password2', TEST_PASSWORD)
USER_DOCTOR_FACTORY_DICT.setdefault('password2', TEST_PASSWORD)
USER_ADMIN_FACTORY_DICT.setdefault('password2', TEST_PASSWORD)
