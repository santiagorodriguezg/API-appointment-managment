"""Users URLs"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.api.views.auth import SignUpAPI, LoginAPI, LogoutAPI
from apps.users.api.views.users import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('signup', SignUpAPI.as_view(), name='signup'),
    path('login', LoginAPI.as_view(), name='login'),
    path('logout', LogoutAPI.as_view(), name='logout'),
]
