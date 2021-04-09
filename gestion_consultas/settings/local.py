"""Development settings."""

from .base import *  # NOQA

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = (Path(BASE_DIR, 'static'),)  # NOQA

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 2,
}
