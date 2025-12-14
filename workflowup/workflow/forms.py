"""
Forms for the workflow app.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Workflow, PlanPruebaQA


class WorkflowCreateForm(forms.ModelForm):
    """
    Form for creating a new workflow.
    jefe_proyecto is set automatically from request.user in the view.
    """

    class Meta:
        model = Workflow
        fields = ['id_proyecto', 'nom_proyecto', 'desc_proyecto', 'componente', 'qa_estimado', 'pap_estimado', 'release']
        widgets = {
            'id_proyecto': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ej: PRJ-001'
            }),
            'nom_proyecto': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Nombre del proyecto'
            }),
            'desc_proyecto': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Descripción detallada del proyecto'
            }),
            'componente': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ej: Frontend, Backend, API'
            }),
            'qa_estimado': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
            'pap_estimado': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
            'release': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Opcional - Ej: v1.0.0'
            }),
        }
        labels = {
            'id_proyecto': 'ID Proyecto',
            'nom_proyecto': 'Nombre Proyecto',
            'desc_proyecto': 'Descripción Proyecto',
            'componente': 'Componente',
            'qa_estimado': 'Fecha QA Estimado',
            'pap_estimado': 'Fecha PAP Estimado',
            'release': 'Release (Opcional)',
        }

    def clean(self):
        """
        Validate that pap_estimado > qa_estimado
        """
        cleaned_data = super().clean()
        qa_estimado = cleaned_data.get('qa_estimado')
        pap_estimado = cleaned_data.get('pap_estimado')

        if qa_estimado and pap_estimado:
            if pap_estimado <= qa_estimado:
                raise ValidationError({
                    'pap_estimado': 'La fecha PAP Estimado debe ser posterior a la fecha QA Estimado.'
                })

        return cleaned_data


class PlanPruebaCreateForm(forms.ModelForm):
    """
    Form for adding a test to a workflow's test plan.
    id_prueba is set automatically as correlative in the view.
    """

    class Meta:
        model = PlanPruebaQA
        fields = ['prueba']
        widgets = {
            'prueba': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Descripción de la prueba',
                'maxlength': 80
            }),
        }
        labels = {
            'prueba': 'Descripción de la Prueba',
        }


class ReleaseUpdateForm(forms.ModelForm):
    """
    Form for updating the release field of a workflow.
    """

    class Meta:
        model = Workflow
        fields = ['release']
        widgets = {
            'release': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ej: v1.0.0'
            }),
        }
        labels = {
            'release': 'Release',
        }


class LineaBaseUpdateForm(forms.ModelForm):
    """
    Form for updating the linea_base field of a workflow (SCM role).
    """

    class Meta:
        model = Workflow
        fields = ['linea_base']
        widgets = {
            'linea_base': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ej: baseline-v1.0.0',
                'maxlength': 80
            }),
        }
        labels = {
            'linea_base': 'Línea Base',
        }


class FechasUpdateForm(forms.ModelForm):
    """
    Form for updating QA and PAP estimated dates (Jefe de Proyecto only).
    """

    class Meta:
        model = Workflow
        fields = ['qa_estimado', 'pap_estimado']
        widgets = {
            'qa_estimado': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
            'pap_estimado': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
        }
        labels = {
            'qa_estimado': 'Fecha QA Estimado',
            'pap_estimado': 'Fecha PAP Estimado',
        }

    def clean(self):
        """
        Validate that pap_estimado > qa_estimado
        """
        cleaned_data = super().clean()
        qa_estimado = cleaned_data.get('qa_estimado')
        pap_estimado = cleaned_data.get('pap_estimado')

        if qa_estimado and pap_estimado:
            if pap_estimado <= qa_estimado:
                raise ValidationError({
                    'pap_estimado': 'La fecha PAP Estimado debe ser posterior a la fecha QA Estimado.'
                })

        return cleaned_data


class CodigoRMUpdateForm(forms.ModelForm):
    """
    Form for updating the codigo_rm field of a workflow (Release Manager role).
    Allows any characters including symbols.
    """

    class Meta:
        model = Workflow
        fields = ['codigo_rm']
        widgets = {
            'codigo_rm': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ej: RM-2024-01',
                'maxlength': '9'
            }),
        }
        labels = {
            'codigo_rm': 'Código RM',
        }
