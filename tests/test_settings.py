"""Testing settings."""

from datetime import timedelta

from gestion_consultas.settings.base import *  # NOQA

# Admin
ADMIN_URL = 'admin/'

SECRET_KEY = 'fake-key_55a6deb597bddea3'

DEBUG = False

# Passwords
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 2,
}

# SIMPLE JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,

    'ALGORITHM': 'HS256',

    'USER_ID_FIELD': 'username',
    'USER_ID_CLAIM': 'user_username',

    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=2),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Django channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
