"""
URL configuration for users_admin app.
"""
from django.urls import path
from . import views

app_name = 'users_admin'

urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path('crear/', views.UserCreateView.as_view(), name='user_create'),
    path('<int:pk>/editar/', views.UserUpdateView.as_view(), name='user_update'),
]
