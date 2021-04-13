"""Appointments factory"""

from datetime import timedelta

import factory
from django.utils import timezone
from factory.fuzzy import FuzzyInteger

from apps.appointments.models import Appointment
from tests.users.factory import UserFactory


class AppointmentFactory(factory.django.DjangoModelFactory):
    """
    Appointment factory.
    Creates a user when an instance is created.
    """

    class Meta:
        model = Appointment

    children = factory.List([
        factory.Dict({
            'name': factory.Faker('name'),
            'age': FuzzyInteger(1, 18)
        }) for _ in range(2)
    ])
    aggressor = factory.Faker('name')
    description = factory.Faker('text')
    start_date = factory.LazyFunction(timezone.now)
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=2))
    user = factory.SubFactory(UserFactory)


APPOINTMENT_FACTORY_DICT = factory.build(dict, FACTORY_CLASS=AppointmentFactory)
