"""Users URLs"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.api.views.accounts import AccountsViewSet
from apps.users.api.views.users import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'accounts', AccountsViewSet, basename='accounts')

urlpatterns = [
    path('', include(router.urls)),
]
