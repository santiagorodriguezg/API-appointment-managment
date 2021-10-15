"""Chats API URLs"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.api.urls import user_url
from apps.chats.api.views.messages import MessageListViewSet
from apps.chats.api.views.rooms import RoomListViewSet

router = DefaultRouter()

router.register(
    f'{user_url}/rooms',
    RoomListViewSet,
    basename='users-rooms'
)

router.register(
    f'{user_url}/rooms/(?P<name>[^/.]+)/messages',
    MessageListViewSet,
    basename='users-messages'
)

urlpatterns = [
    path('v1/', include(router.urls)),
]
