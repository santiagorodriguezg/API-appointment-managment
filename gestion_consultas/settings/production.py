"""Production settings."""

from .base import *  # NOQA

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = Path(BASE_DIR, 'static')  # NOQA

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
