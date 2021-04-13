"""Appointments URLs"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.appointments.api.views.appointments import AppointmentViewSet, AppointmentListAPIView

router = DefaultRouter()
router.register(
    r'users/(?P<username>[-a-zA-Z0-0_]+)/appointments',
    AppointmentViewSet,
    basename='appointments'
)

urlpatterns = [
    path('', include(router.urls)),
    path('appointments/', AppointmentListAPIView.as_view(), name='appointments'),
]
