"""Accounts URLs"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apps.accounts.api.views.accounts import (
    PasswordResetEmailAPIView, PasswordResetVerifyTokenAPIView, PasswordResetCompleteAPIView, SignupAPIView,
    LoginAPIView, LogoutAPIView
)
from apps.accounts.api.views.users import UserModelViewSet

router = DefaultRouter()
router.register(r'v1/users', UserModelViewSet, basename='users')

user_url = r'users/(?P<username>[-a-zA-Z0-0_]+)'

urlpatterns = [
    path('', include(router.urls)),
    path('v1/signup/', SignupAPIView.as_view(), name='signup'),
    path('v1/login/', LoginAPIView.as_view(), name='login'),
    path('v1/logout/', LogoutAPIView.as_view(), name='logout'),

    path('v1/password/reset/', PasswordResetEmailAPIView.as_view(), name="password_reset_email"),
    path(
        'v1/password/reset/<uidb64>/<token>/',
        PasswordResetVerifyTokenAPIView.as_view(),
        name='password_reset_verify_token'
    ),
    path('v1/password/reset/complete/', PasswordResetCompleteAPIView.as_view(), name='password_reset_complete'),

    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
