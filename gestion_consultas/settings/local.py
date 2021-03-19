from .base import *

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
FILE_UPLOAD_PERMISSIONS = 0o644
STATICFILES_DIRS = (Path(BASE_DIR, 'static'),)

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
