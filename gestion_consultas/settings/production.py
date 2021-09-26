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
    'USER_ID_FIELD': 'username',
    'USER_ID_CLAIM': 'user_username',
}

# A list of hex-encoded 32 byte keys
# You only need one unless / until rotating keys
# https://gitlab.com/guywillett/django-searchable-encrypted-fields/-/tree/master#rotating-encryption-keys
FIELD_ENCRYPTION_KEYS = config('FIELD_ENCRYPTION_KEYS', cast=Csv()) # NOQA

# Django channels
# https://pypi.org/project/channels-redis/
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [f"redis://:{config('REDIS_PASSWORD')}@127.0.0.1:6379/0"], # NOQA
            "symmetric_encryption_keys": config('REDIS_SYMMETRIC_ENCRYPTION_KEYS', cast=Csv()), # NOQA
        },
    },
}
