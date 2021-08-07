"""Accounts URLs"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apps.accounts.api.views.accounts import AccountsViewSet
from apps.accounts.api.views.users import UserModelViewSet

router = DefaultRouter()
router.register(r'accounts', AccountsViewSet, basename='accounts')
router.register(r'v1/users', UserModelViewSet, basename='users')

user_url = r'users/(?P<username>[-a-zA-Z0-0_]+)'

urlpatterns = [
    path('', include(router.urls)),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
