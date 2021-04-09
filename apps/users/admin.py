from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ('created_at', 'updated_at', 'last_login')
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'identification']
    list_display = (
        'id', 'get_full_name', 'email', 'phone', 'identification_number', 'is_active', 'is_staff', 'created_at'
    )
