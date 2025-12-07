"""
Views for the workflow app.
Main application area accessible to all authenticated users.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    """
    Main workflow dashboard.
    Shows user information and will contain workflow/project management features.
    """
    context = {
        'user': request.user,
    }
    return render(request, 'workflow/dashboard.html', context)
