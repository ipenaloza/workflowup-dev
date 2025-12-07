from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model.
    Extends Django's default UserAdmin to include role field.
    """

    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('role',)}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('first_name', 'last_name', 'email', 'role'),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of users through admin interface."""
        return False
