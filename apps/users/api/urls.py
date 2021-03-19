"""Users URLs"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, LoginAPI

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('login', LoginAPI.as_view(), name='login')
]
