"""
Views for the workflow app.
Main application area accessible to all authenticated users.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Max, Q
from django.http import JsonResponse
from django.utils import timezone
from .models import Workflow, PlanPruebaQA, Actividad
from .forms import WorkflowCreateForm, PlanPruebaCreateForm, ReleaseUpdateForm


@login_required
def dashboard(request):
    """
    Main workflow dashboard.
    Routes to different templates based on user role.
    """
    if request.user.role == 'Jefe de Proyecto':
        # Get workflows for this project manager
        workflows = Workflow.objects.filter(
            jefe_proyecto=request.user.username
        ).prefetch_related('actividades')

        # Apply filters from GET parameters
        id_proyecto = request.GET.get('id_proyecto', '').strip()
        estado_filtro = request.GET.get('estado', '').strip()
        fecha_desde = request.GET.get('fecha_desde', '').strip()
        fecha_hasta = request.GET.get('fecha_hasta', '').strip()

        # Filter by id_proyecto (exact match)
        if id_proyecto:
            workflows = workflows.filter(id_proyecto=id_proyecto)

        # Filter by date range
        if fecha_desde:
            workflows = workflows.filter(creacion__gte=fecha_desde)
        if fecha_hasta:
            workflows = workflows.filter(creacion__lte=fecha_hasta)

        # Filter out workflows with estado_workflow = 'Cancelado' or 'Cerrado'
        # Also apply estado filter if provided
        active_workflows = []
        for workflow in workflows:
            ultima_actividad = workflow.get_actividad_workflow()
            if ultima_actividad:
                # Exclude Cancelado and Cerrado
                if ultima_actividad.estado_workflow not in ['Cancelado', 'Cerrado']:
                    # Apply estado filter if provided
                    if estado_filtro:
                        if ultima_actividad.estado_workflow == estado_filtro:
                            active_workflows.append(workflow)
                    else:
                        active_workflows.append(workflow)
            else:
                # No activities yet, include it (estado would be N/A)
                if not estado_filtro:  # Only include if no estado filter
                    active_workflows.append(workflow)

        # Prepare data for display
        workflow_data = []
        for workflow in active_workflows:
            ultima_actividad = workflow.get_actividad_workflow()
            workflow_data.append({
                'workflow': workflow,
                'estado_workflow': ultima_actividad.estado_workflow if ultima_actividad else 'N/A',
                'proceso': ultima_actividad.proceso if ultima_actividad else 'N/A',
                'estado_proceso': ultima_actividad.estado_proceso if ultima_actividad else 'N/A',
            })

        # Get unique project IDs for filter dropdown
        # Get all workflows for this jefe (without date/estado filters) to build the project list
        all_workflows = Workflow.objects.filter(
            jefe_proyecto=request.user.username
        ).prefetch_related('actividades')

        project_ids = set()
        for workflow in all_workflows:
            ultima_actividad = workflow.get_actividad_workflow()
            if ultima_actividad:
                if ultima_actividad.estado_workflow in ['Nuevo', 'Activo']:
                    project_ids.add(workflow.id_proyecto)
            else:
                # No activities yet, consider it as active
                project_ids.add(workflow.id_proyecto)

        # Sort project IDs alphabetically
        project_ids_sorted = sorted(project_ids)

        context = {
            'workflow_data': workflow_data,
            'project_ids': project_ids_sorted,
        }
        return render(request, 'workflow/dashboard_jp.html', context)

    # Default dashboard for other roles
    context = {
        'user': request.user,
    }
    return render(request, 'workflow/dashboard.html', context)


@login_required
def workflow_create(request):
    """
    Create a new workflow (Jefe de Proyecto only).
    """
    if request.user.role != 'Jefe de Proyecto':
        raise PermissionDenied("Solo los Jefes de Proyecto pueden crear workflows.")

    if request.method == 'POST':
        form = WorkflowCreateForm(request.POST)
        if form.is_valid():
            # Create workflow
            workflow = form.save(commit=False)
            workflow.jefe_proyecto = request.user.username
            workflow.save()

            # Create initial activity
            Actividad.objects.create(
                workflow=workflow,
                id_actividad=1,
                usuario=request.user.username,
                estado_workflow='Nuevo',
                proceso=None,
                estado_proceso=None,
                actividad='Workflow creado satisfactoriamente',
                comentario=None
            )

            messages.success(request, f'Workflow {workflow.id_workflow} creado exitosamente.')
            return redirect('workflow:dashboard')
    else:
        form = WorkflowCreateForm()

    context = {
        'form': form,
    }
    return render(request, 'workflow/workflow_create.html', context)


@login_required
def workflow_detail(request, id_workflow):
    """
    View workflow details (only accessible by the workflow's jefe_proyecto).
    Handles release updates and activity creation.
    """
    workflow = get_object_or_404(Workflow, id_workflow=id_workflow)

    # Verify user is the jefe de proyecto
    if request.user.username != workflow.jefe_proyecto:
        raise PermissionDenied("Solo el jefe de proyecto puede ver este workflow.")

    # Handle release update
    if request.method == 'POST' and 'update_release' in request.POST:
        release_form = ReleaseUpdateForm(request.POST, instance=workflow)
        if release_form.is_valid():
            release_form.save()
            messages.success(request, 'Release actualizado exitosamente.')
            return redirect('workflow:workflow_detail', id_workflow=id_workflow)

    # Handle workflow cancellation
    if request.method == 'POST' and 'cancel_workflow' in request.POST:
        # Get the next id_actividad
        max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
        next_id = (max_id or 0) + 1

        # Create cancellation activity
        Actividad.objects.create(
            workflow=workflow,
            id_actividad=next_id,
            usuario=request.user.username,
            estado_workflow='Cancelado',
            proceso=None,
            estado_proceso=None,
            actividad='Workflow Cancelado',
            comentario=None
        )

        messages.success(request, 'Workflow cancelado exitosamente.')
        return redirect('workflow:workflow_detail', id_workflow=id_workflow)

    # Handle process requests (linea base, RM Rev, Diff Info, QA)
    if request.method == 'POST' and 'proceso_request' in request.POST:
        proceso = request.POST.get('proceso')
        comentario = request.POST.get('comentario', '')

        # Get the next id_actividad
        max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
        next_id = (max_id or 0) + 1

        # Determine if it's a re-request
        ultima_actividad = workflow.get_actividad_workflow()
        is_rechazo = False

        if proceso == 'linea base':
            actividad_scm1 = workflow.get_actividad_scm1()
            is_rechazo = actividad_scm1 and actividad_scm1.estado_proceso == 'No Ok'
            actividad_text = 'Re solicitud de linea base' if is_rechazo else 'Linea base solicitada'
        elif proceso == 'RM Rev':
            actividad_rm = workflow.get_actividad_rm()
            is_rechazo = actividad_rm and actividad_rm.estado_proceso == 'No Ok'
            actividad_text = 'Re solicitud de Revision RM' if is_rechazo else 'Revision RM solicitada'
        elif proceso == 'Diff Info':
            actividad_scm2 = workflow.get_actividad_scm2()
            is_rechazo = actividad_scm2 and actividad_scm2.estado_proceso == 'No Ok'
            actividad_text = 'Re solicitud de Informe diferencias' if is_rechazo else 'Informe diferencias solicitado'
        elif proceso == 'QA':
            actividad_qa = workflow.get_actividad_qa()
            is_rechazo = actividad_qa and actividad_qa.estado_proceso == 'No Ok'
            actividad_text = 'Re solicitud de pruebas QA' if is_rechazo else 'Pruebas QA solicitadas'
        else:
            messages.error(request, 'Proceso no válido.')
            return redirect('workflow:workflow_detail', id_workflow=id_workflow)

        # Create the activity
        Actividad.objects.create(
            workflow=workflow,
            id_actividad=next_id,
            usuario=request.user.username,
            estado_workflow='Activo',
            proceso=proceso,
            estado_proceso='En Proceso',
            actividad=actividad_text,
            comentario=comentario if comentario else None
        )

        messages.success(request, f'{actividad_text} exitosamente.')
        return redirect('workflow:workflow_detail', id_workflow=id_workflow)

    # Get all activities for display
    actividades = workflow.actividades.all()

    # Get process states for button enabling
    actividad_workflow = workflow.get_actividad_workflow()
    actividad_scm1 = workflow.get_actividad_scm1()
    actividad_rm = workflow.get_actividad_rm()
    actividad_scm2 = workflow.get_actividad_scm2()
    actividad_qa = workflow.get_actividad_qa()

    # Determine button states
    # Button 1: Solicitar línea base
    # DEBE estar deshabilitado cuando:
    # - El campo release está vacío/null
    # - Ya existe una línea base aprobada (estado_proceso='Ok')
    btn1_enabled = (
        workflow.release and  # release debe estar lleno
        workflow.release.strip() and  # y no ser solo espacios en blanco
        not (actividad_scm1 and actividad_scm1.estado_proceso == 'Ok') and  # no tener línea base aprobada
        (
            (not actividad_scm1) or  # primera solicitud
            (actividad_scm1 and actividad_scm1.estado_proceso == 'No Ok')  # o fue rechazada
        )
    )

    # Button 2: Solicitar revisión RM
    btn2_enabled = (
        (actividad_scm1 and actividad_scm1.estado_proceso == 'Ok') or
        (actividad_rm and actividad_rm.estado_proceso == 'No Ok')
    )

    # Button 3: Solicitar Informe de diferencia
    btn3_enabled = (
        (actividad_rm and actividad_rm.estado_proceso == 'Ok') or
        (actividad_scm2 and actividad_scm2.estado_proceso == 'No Ok')
    )

    # Button 4: Solicitar Pruebas de QA
    btn4_enabled = (
        (actividad_scm2 and actividad_scm2.estado_proceso == 'Ok') or
        (actividad_qa and actividad_qa.estado_proceso == 'No Ok')
    )

    context = {
        'workflow': workflow,
        'actividades': actividades,
        'actividad_workflow': actividad_workflow,
        'actividad_scm1': actividad_scm1,
        'actividad_rm': actividad_rm,
        'actividad_scm2': actividad_scm2,
        'actividad_qa': actividad_qa,
        'btn1_enabled': btn1_enabled,
        'btn2_enabled': btn2_enabled,
        'btn3_enabled': btn3_enabled,
        'btn4_enabled': btn4_enabled,
        'release_form': ReleaseUpdateForm(instance=workflow),
    }
    return render(request, 'workflow/workflow_detail.html', context)


@login_required
def plan_pruebas(request, id_workflow):
    """
    View and manage test plan for a workflow.
    """
    workflow = get_object_or_404(Workflow, id_workflow=id_workflow)

    # Verify user is the jefe de proyecto
    if request.user.username != workflow.jefe_proyecto:
        raise PermissionDenied("Solo el jefe de proyecto puede ver este plan de pruebas.")

    if request.method == 'POST':
        form = PlanPruebaCreateForm(request.POST)
        if form.is_valid():
            # Get next id_prueba
            max_id = workflow.plan_pruebas.aggregate(Max('id_prueba'))['id_prueba__max']
            next_id = (max_id or 0) + 1

            # Create the test
            prueba = form.save(commit=False)
            prueba.workflow = workflow
            prueba.id_prueba = next_id
            prueba.avance = '0%'
            prueba.resultado = 'No iniciado'
            prueba.save()

            messages.success(request, f'Prueba {next_id} agregada exitosamente.')
            return redirect('workflow:plan_pruebas', id_workflow=id_workflow)
    else:
        form = PlanPruebaCreateForm()

    # Get all tests for this workflow
    pruebas = workflow.plan_pruebas.all()

    context = {
        'workflow': workflow,
        'pruebas': pruebas,
        'form': form,
    }
    return render(request, 'workflow/plan_pruebas.html', context)
