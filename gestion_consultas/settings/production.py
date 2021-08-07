"""Production settings."""

from datetime import timedelta

from .base import *  # NOQA

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = Path(BASE_DIR, '../static')  # NOQA

# Security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 25,
}

# SIMPLE JWT
# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=5),
    'ROTATE_REFRESH_TOKENS': True,

    'USER_ID_FIELD': 'username',
    'USER_ID_CLAIM': 'user_username',

    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=15),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=5),
}

# A list of hex-encoded 32 byte keys
# You only need one unless / until rotating keys
# https://gitlab.com/guywillett/django-searchable-encrypted-fields/-/tree/master#rotating-encryption-keys
FIELD_ENCRYPTION_KEYS = [
    'd5c1ac291a84327ab3768728f8c656a26b89f88eed61d3befd4d123905453a23',
]

# Django channels
# https://pypi.org/project/channels-redis/
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
