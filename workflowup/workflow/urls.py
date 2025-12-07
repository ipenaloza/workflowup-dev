"""
URL configuration for workflow app.
"""
from django.urls import path
from . import views

app_name = 'workflow'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
