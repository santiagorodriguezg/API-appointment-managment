"""gestion_consultas URL configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('chat/', include('apps.chats.urls')),  # Solo para probar el chat
    path('api/', include('apps.accounts.api.urls'), name='accounts'),
    path('api/', include('apps.appointments.api.urls'), name='appointments'),
    path('api/', include('apps.chats.api.urls'), name='chats'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
