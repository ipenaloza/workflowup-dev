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
    path('<int:id_workflow>/qa/', views.workflow_detail_qa, name='workflow_detail_qa'),
    path('<int:id_workflow>/qa/<int:id_prueba>/update-avance/', views.qa_update_avance_ajax, name='qa_update_avance_ajax'),
    path('<int:id_workflow>/qa/<int:id_prueba>/toggle-rechazar/', views.qa_toggle_rechazar_ajax, name='qa_toggle_rechazar_ajax'),
]
