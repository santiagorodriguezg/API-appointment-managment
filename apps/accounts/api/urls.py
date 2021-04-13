"""Accounts URLs"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.api.views.accounts import AccountsViewSet
from apps.accounts.api.views.users import UserModelViewSet

router = DefaultRouter()
router.register(r'accounts', AccountsViewSet, basename='accounts')
router.register(r'users', UserModelViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
