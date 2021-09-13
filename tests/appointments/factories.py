"""Appointments factories"""

from datetime import timedelta

import factory
from django.utils import timezone
from factory.fuzzy import FuzzyInteger, FuzzyChoice

from apps.appointments.models import Appointment
from tests.accounts.factories import UserFactory


class AppointmentFactory(factory.django.DjangoModelFactory):
    """
    Appointment factory.
    Creates a user when an instance is created.
    """

    class Meta:
        model = Appointment

    type = FuzzyChoice(choices=Appointment.APPOINTMENT_TYPE_CHOICES, getter=lambda c: c[0])
    children = factory.List([
        factory.Dict({
            'name': factory.Faker('name'),
            'age': FuzzyInteger(1, 18),
        }) for _ in range(2)
    ])
    aggressor = factory.List([
        factory.Dict({
            'name': factory.Faker('name'),
            'age': FuzzyInteger(1, 18),
            'identification_number': factory.Faker('bothify', text='########'),
            'phone': factory.Faker('bothify', text='3#########'),
            'address': factory.Faker('address'),
            'more_info': factory.Faker('sentence'),
        })
    ])
    description = factory.Faker('text')
    start_date = factory.LazyFunction(timezone.now)
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=2))
    user = factory.SubFactory(UserFactory)


APPOINTMENT_FACTORY_DICT = factory.build(dict, FACTORY_CLASS=AppointmentFactory)
