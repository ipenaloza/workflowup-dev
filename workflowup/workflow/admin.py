from django.contrib import admin
from .models import Workflow, PlanPruebaQA, Actividad


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['id_workflow', 'id_proyecto', 'nom_proyecto', 'jefe_proyecto', 'componente', 'creacion', 'qa_estimado', 'pap_estimado']
    list_filter = ['creacion', 'jefe_proyecto']
    search_fields = ['id_proyecto', 'nom_proyecto', 'jefe_proyecto', 'componente']
    readonly_fields = ['creacion']
    ordering = ['-creacion']


@admin.register(PlanPruebaQA)
class PlanPruebaQAAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'id_prueba', 'prueba', 'avance', 'resultado']
    list_filter = ['resultado', 'workflow']
    search_fields = ['prueba', 'workflow__nom_proyecto']
    ordering = ['workflow', 'id_prueba']


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'id_actividad', 'fecha', 'usuario', 'estado_workflow', 'proceso', 'estado_proceso', 'actividad']
    list_filter = ['fecha', 'estado_workflow', 'proceso', 'estado_proceso']
    search_fields = ['usuario', 'actividad', 'workflow__nom_proyecto']
    readonly_fields = ['fecha']
    ordering = ['-fecha']
