"""Appointments URLs"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.api.urls import user_url
from apps.appointments.api.views.appointments import AppointmentViewSet, AppointmentListViewSet

router = DefaultRouter()
router.register('appointments', AppointmentListViewSet, basename='appointments-list')
router.register(f'{user_url}/appointments', AppointmentViewSet, basename='users-appointments')

urlpatterns = [
    path('v1/', include(router.urls)),
]
