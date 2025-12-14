"""
URL configuration for workflow app.
"""
from django.urls import path
from . import views

app_name = 'workflow'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.workflow_create, name='workflow_create'),
    path('<int:id_workflow>/', views.workflow_detail, name='workflow_detail'),
    path('<int:id_workflow>/plan-pruebas/', views.plan_pruebas, name='plan_pruebas'),
    path('<int:id_workflow>/scm/', views.workflow_detail_scm, name='workflow_detail_scm'),
    path('<int:id_workflow>/rm/', views.workflow_detail_rm, name='workflow_detail_rm'),
]
