"""Production settings."""

from datetime import timedelta

from .base import *  # NOQA

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR.parent / 'static'  # NOQA

# Databases
DATABASES['default']['CONN_MAX_AGE'] = config('DB_CONN_MAX_AGE', default=60, cast=int)  # NOQA

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),  # NOQA
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

# https://docs.djangoproject.com/en/3.2/ref/settings/#secure-ssl-redirect
# SECURE_SSL_REDIRECT=True

# https://docs.djangoproject.com/en/3.2/ref/settings/#secure-hsts-seconds
# SECURE_HSTS_SECONDS=0


# Admin

# A list of all the people who get code error notifications.
# https://docs.djangoproject.com/en/3.2/ref/settings/#admins
# ADMINS = [('John', 'john@example.com'), ('Mary', 'mary@example.com')]

# A list of all the people who should get broken link notifications.
# https://docs.djangoproject.com/en/3.2/ref/settings/#managers
# MANAGERS = ADMINS

# By default, Django will send system email from root@localhost.
# However, some mail providers reject all email from this address.
# https://docs.djangoproject.com/en/3.2/ref/settings/#server-email
# SERVER_EMAIL = webmaster@example.com

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}

# SIMPLE JWT
# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    'ALGORITHM': 'HS256',
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=5),
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=15),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=5),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'USER_ID_FIELD': 'username',
    'USER_ID_CLAIM': 'user_username',
}

# A list of hex-encoded 32 byte keys
# You only need one unless / until rotating keys
# https://gitlab.com/guywillett/django-searchable-encrypted-fields/-/tree/master#rotating-encryption-keys
FIELD_ENCRYPTION_KEYS = config('FIELD_ENCRYPTION_KEYS', cast=Csv())  # NOQA

# Django channels
# https://pypi.org/project/channels-redis/
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [config('REDIS_URL')],  # NOQA
            "symmetric_encryption_keys": config('REDIS_SYMMETRIC_ENCRYPTION_KEYS', cast=Csv()),  # NOQA
        },
    },
}
