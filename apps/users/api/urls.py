"""Users URLs"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LogoutAPI, LoginAPI, UserViewSet, SignUpAPI

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', LogoutAPI.as_view(), name='logout'),
    path('signup/', SignUpAPI.as_view(), name='signup'),
]
