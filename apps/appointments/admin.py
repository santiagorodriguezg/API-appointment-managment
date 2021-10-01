"""Appointments admin"""

from django.contrib import admin

from .models import Appointment, AppointmentMultimedia

admin.site.register(Appointment)
admin.site.register(AppointmentMultimedia)
