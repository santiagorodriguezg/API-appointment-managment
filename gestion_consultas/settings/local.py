"""Development settings."""

import re
from datetime import timedelta

from .base import *  # NOQA

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = (Path(BASE_DIR, '../static'),)  # NOQA

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 2,
}

# SIMPLE JWT
# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    'ALGORITHM': 'HS256',
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=10),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'USER_ID_FIELD': 'username',
    'USER_ID_CLAIM': 'user_username',
}

# A list of hex-encoded 32 byte keys
# You only need one unless / until rotating keys
# https://gitlab.com/guywillett/django-searchable-encrypted-fields/-/tree/master#rotating-encryption-keys
FIELD_ENCRYPTION_KEYS = config('FIELD_ENCRYPTION_KEYS', cast=Csv())

# Django channels
# https://pypi.org/project/channels-redis/
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
