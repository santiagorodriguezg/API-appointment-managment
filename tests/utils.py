"""Testing utilities"""

from faker import Faker

from apps.accounts.models import User

fake = Faker(['es_ES'])

TEST_PASSWORD = 'sr123456'

USER_DATA = {
    'role': User.Type.DOCTOR,
    'first_name': fake.last_name(),
    'last_name': fake.last_name(),
    'identification_type': User.IdentificationType.CC,
    'identification_number': fake.bothify(text='########'),
    'username': fake.last_name(),
    'email': fake.free_email(),
    'phone': fake.bothify(text='3#########'),
    'city': fake.city(),
    'neighborhood': fake.street_name(),
    'address': fake.street_address(),
    'password': TEST_PASSWORD,
    'password2': TEST_PASSWORD,
}
