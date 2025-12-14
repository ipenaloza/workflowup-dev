from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Workflow(models.Model):
    """
    Main workflow model for managing software release workflows.
    Each workflow is associated with a project manager (Jefe de Proyecto).
    """

    id_workflow = models.AutoField(primary_key=True)
    id_proyecto = models.CharField(max_length=8, verbose_name='ID Proyecto')
    nom_proyecto = models.CharField(max_length=70, verbose_name='Nombre Proyecto')
    jefe_proyecto = models.CharField(max_length=15, verbose_name='Jefe de Proyecto')  # username
    desc_proyecto = models.TextField(verbose_name='Descripción Proyecto')
    componente = models.CharField(max_length=30, verbose_name='Componente')
    linea_base = models.CharField(max_length=80, blank=True, null=True, verbose_name='Línea Base')
    codigo_rm = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        verbose_name='Código RM'
    )
    release = models.CharField(max_length=80, blank=True, null=True, verbose_name='Release')
    creacion = models.DateField(auto_now_add=True, verbose_name='Fecha Creación')
    qa_estimado = models.DateField(verbose_name='QA Estimado')
    pap_estimado = models.DateField(verbose_name='PAP Estimado')

    class Meta:
        ordering = ['-creacion']
        verbose_name = 'Workflow'
        verbose_name_plural = 'Workflows'

    def __str__(self):
        return f"{self.id_workflow} - {self.nom_proyecto}"

    def clean(self):
        """
        Validate that pap_estimado > qa_estimado
        Validate that jefe_proyecto corresponds to an existing user
        """
        if self.pap_estimado and self.qa_estimado:
            if self.pap_estimado <= self.qa_estimado:
                raise ValidationError({
                    'pap_estimado': 'La fecha PAP Estimado debe ser posterior a la fecha QA Estimado.'
                })

        # Validate jefe_proyecto exists
        if self.jefe_proyecto:
            if not User.objects.filter(username=self.jefe_proyecto).exists():
                raise ValidationError({
                    'jefe_proyecto': f'El usuario {self.jefe_proyecto} no existe.'
                })

    # Helper methods to get the latest activities
    def get_actividad_workflow(self):
        """Get the most recent general activity (latest by fecha)"""
        return self.actividades.order_by('-fecha').first()

    def get_actividad_scm1(self):
        """Get the most recent 'linea base' activity"""
        return self.actividades.filter(proceso='linea base').order_by('-fecha').first()

    def get_actividad_rm(self):
        """Get the most recent 'RM Rev' activity"""
        return self.actividades.filter(proceso='RM Rev').order_by('-fecha').first()

    def get_actividad_scm2(self):
        """Get the most recent 'Diff Info' activity"""
        return self.actividades.filter(proceso='Diff Info').order_by('-fecha').first()

    def get_actividad_qa(self):
        """Get the most recent 'QA' activity"""
        return self.actividades.filter(proceso='QA').order_by('-fecha').first()


class PlanPruebaQA(models.Model):
    """
    QA Test Plan associated with a workflow.
    Each test has a sequential id_prueba per workflow.
    """

    RESULTADO_CHOICES = [
        ('No iniciado', 'No iniciado'),
        ('En proceso', 'En proceso'),
        ('Aprobado', 'Aprobado'),
        ('No aprobado', 'No aprobado'),
    ]

    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='plan_pruebas',
        verbose_name='Workflow'
    )
    id_prueba = models.PositiveSmallIntegerField(verbose_name='ID Prueba')
    prueba = models.CharField(max_length=80, verbose_name='Prueba')
    avance = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Avance'
    )
    resultado = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES,
        default='No iniciado',
        verbose_name='Resultado'
    )

    class Meta:
        ordering = ['id_prueba']
        unique_together = [['workflow', 'id_prueba']]
        verbose_name = 'Plan de Prueba QA'
        verbose_name_plural = 'Planes de Prueba QA'

    def __str__(self):
        return f"{self.workflow.id_workflow} - Prueba {self.id_prueba}: {self.prueba}"


class Actividad(models.Model):
    """
    Activity log for workflow tracking.
    Records all state changes and process transitions.
    """

    ESTADO_WORKFLOW_CHOICES = [
        ('Nuevo', 'Nuevo'),
        ('Activo', 'Activo'),
        ('Cancelado', 'Cancelado'),
        ('Cerrado', 'Cerrado'),
    ]

    PROCESO_CHOICES = [
        ('linea base', 'Línea Base'),
        ('RM Rev', 'Revisión RM'),
        ('Diff Info', 'Informe Diferencias'),
        ('QA', 'Pruebas QA'),
    ]

    ESTADO_PROCESO_CHOICES = [
        ('No Iniciado', 'No Iniciado'),
        ('En Proceso', 'En Proceso'),
        ('Ok', 'Ok'),
        ('No Ok', 'No Ok'),
    ]

    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='actividades',
        verbose_name='Workflow'
    )
    id_actividad = models.PositiveIntegerField(verbose_name='ID Actividad')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    usuario = models.CharField(max_length=15, verbose_name='Usuario')  # username
    estado_workflow = models.CharField(
        max_length=20,
        choices=ESTADO_WORKFLOW_CHOICES,
        null=True,
        blank=True,
        verbose_name='Estado Workflow'
    )
    proceso = models.CharField(
        max_length=20,
        choices=PROCESO_CHOICES,
        null=True,
        blank=True,
        verbose_name='Proceso'
    )
    estado_proceso = models.CharField(
        max_length=20,
        choices=ESTADO_PROCESO_CHOICES,
        null=True,
        blank=True,
        verbose_name='Estado Proceso'
    )
    actividad = models.CharField(max_length=35, verbose_name='Actividad')
    comentario = models.CharField(max_length=200, blank=True, null=True, verbose_name='Comentario')

    class Meta:
        ordering = ['-fecha']
        unique_together = [['workflow', 'id_actividad']]
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f"{self.workflow.id_workflow} - Actividad {self.id_actividad}: {self.actividad}"
