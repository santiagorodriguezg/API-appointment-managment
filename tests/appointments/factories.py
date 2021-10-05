"""Appointments factories"""

from datetime import timedelta

import factory
from factory.fuzzy import FuzzyInteger, FuzzyChoice
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentMultimedia
from tests.accounts.factories import UserFactory
from tests.utils import TEST_AUDIO_FILE_NAME, TEST_PDF_FILE_NAME, TEST_IMG_FILE_NAME


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
    aggressor = factory.Dict({
        'name': factory.Faker('name'),
        'age': FuzzyInteger(1, 18),
        'identification_number': factory.Faker('bothify', text='########'),
        'phone': factory.Faker('bothify', text='3#########'),
        'address': factory.Faker('address'),
        'more_info': factory.Faker('sentence'),
    })
    audio = factory.django.FileField(from_path=f'tests/files/audio/{TEST_AUDIO_FILE_NAME}.mp3')
    description = factory.Faker('text')
    start_date = factory.LazyFunction(timezone.now)
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=2))
    user = factory.SubFactory(UserFactory)


class AppointmentMultimediaIMGFactory(factory.django.DjangoModelFactory):
    """
    Appointment Multimedia IMG factory.
    Generates an image file.
    """

    class Meta:
        model = AppointmentMultimedia

    file = factory.django.ImageField(filename=f'{TEST_IMG_FILE_NAME}.jpg')
    file_type = AppointmentMultimedia.FileType.IMAGE
    appointment = factory.SubFactory(AppointmentFactory)


class AppointmentMultimediaPDFactory(factory.django.DjangoModelFactory):
    """
    Appointment Multimedia PDF factory.
    Generates an PDF file.
    """

    class Meta:
        model = AppointmentMultimedia

    file = factory.django.FileField(from_path=f'tests/files/pdf/{TEST_PDF_FILE_NAME}.pdf')
    file_type = AppointmentMultimedia.FileType.PDF
    appointment = factory.SubFactory(AppointmentFactory)
