"""
Custom decorators for access control in the users_admin app.
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    """
    Decorator that requires the user to be authenticated and have 'Administrador' role.

    Usage:
        @admin_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'Administrador':
            raise PermissionDenied("Solo los administradores pueden acceder a esta página.")
        return view_func(request, *args, **kwargs)
    return wrapper
