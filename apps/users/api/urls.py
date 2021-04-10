"""Users URLs"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.api.views.auth import (
    SignUpAPIView, LoginAPIView, LogoutAPIView, VerifyTokenAPIView, PasswordResetAPIView, PasswordResetFromKeyAPIView,
)
from apps.users.api.views.users import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('signup', SignUpAPIView.as_view(), name='signup'),
    path('login', LoginAPIView.as_view(), name='login'),
    path('logout', LogoutAPIView.as_view(), name='logout'),
    path('verify-token', VerifyTokenAPIView.as_view(), name='verify_token'),
    path('password-reset', PasswordResetAPIView.as_view(), name='password_reset'),
    path('password-reset-key', PasswordResetFromKeyAPIView.as_view(), name='password_reset_from_key'),
]
