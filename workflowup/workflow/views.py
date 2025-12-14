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
from .forms import WorkflowCreateForm, PlanPruebaCreateForm, ReleaseUpdateForm, LineaBaseUpdateForm, FechasUpdateForm, CodigoRMUpdateForm


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

    elif request.user.role == 'SCM':
        # Get all workflows with SCM activities in process
        # "lista de actividades scm": QuerySet where latest activity has:
        # (proceso='linea base' AND estado_proceso='En Proceso') OR
        # (proceso='Diff Info' AND estado_proceso='En Proceso')
        all_workflows = Workflow.objects.all().prefetch_related('actividades')

        scm_workflows = []
        for workflow in all_workflows:
            # Get the latest activity
            ultima_actividad = workflow.get_actividad_workflow()

            # Check if workflow should be included in SCM list
            if ultima_actividad:
                # Include if estado_workflow is 'Activo' (exclude Cancelado/Cerrado)
                if ultima_actividad.estado_workflow == 'Activo':
                    # Check if SCM needs to act on this workflow
                    actividad_scm1 = workflow.get_actividad_scm1()
                    actividad_scm2 = workflow.get_actividad_scm2()

                    # Include if linea base is in process
                    if actividad_scm1 and actividad_scm1.estado_proceso == 'En Proceso':
                        scm_workflows.append({
                            'workflow': workflow,
                            'proceso': 'linea base',
                            'estado_workflow': ultima_actividad.estado_workflow,
                        })
                    # Or if Diff Info is in process
                    elif actividad_scm2 and actividad_scm2.estado_proceso == 'En Proceso':
                        scm_workflows.append({
                            'workflow': workflow,
                            'proceso': 'Diff Info',
                            'estado_workflow': ultima_actividad.estado_workflow,
                        })

        context = {
            'scm_workflows': scm_workflows,
        }
        return render(request, 'workflow/dashboard_scm.html', context)

    elif request.user.role == 'Release Manager':
        # Get all workflows with RM Rev activities in process
        all_workflows = Workflow.objects.all().prefetch_related('actividades')

        rm_workflows = []
        for workflow in all_workflows:
            # Verify general workflow state
            ultima_actividad = workflow.get_actividad_workflow()
            if ultima_actividad and ultima_actividad.estado_workflow == 'Activo':
                # Check if RM Rev process is in progress
                actividad_rm = workflow.get_actividad_rm()
                if actividad_rm and actividad_rm.estado_proceso == 'En Proceso':
                    rm_workflows.append(workflow)

        # Prepare data for display
        workflow_data = []
        for workflow in rm_workflows:
            ultima_actividad = workflow.get_actividad_workflow()
            actividad_rm = workflow.get_actividad_rm()
            workflow_data.append({
                'workflow': workflow,
                'estado_workflow': ultima_actividad.estado_workflow if ultima_actividad else 'N/A',
                'proceso': actividad_rm.proceso if actividad_rm else 'N/A',
                'actividad': actividad_rm.actividad if actividad_rm else 'N/A',
            })

        context = {
            'workflow_data': workflow_data,
        }
        return render(request, 'workflow/dashboard_rm.html', context)

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

    # Handle dates update
    if request.method == 'POST' and 'update_fechas' in request.POST:
        fechas_form = FechasUpdateForm(request.POST, instance=workflow)
        if fechas_form.is_valid():
            fechas_form.save()
            messages.success(request, 'Fechas actualizadas exitosamente.')
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
    # DEBE estar deshabilitado SOLO cuando:
    # - Ya existe una línea base aprobada (proceso='linea base' y estado_proceso='Ok')
    btn1_enabled = not (actividad_scm1 and actividad_scm1.estado_proceso == 'Ok')

    # Button 2: Solicitar revisión RM
    # Debe estar deshabilitado cuando:
    # - El campo release está vacío o null
    # - Ya existe una revisión RM aprobada (estado_proceso='Ok')
    # Debe estar habilitado cuando:
    # - La línea base fue aprobada (scm1 Ok) Y release tiene contenido Y no hay aprobación RM previa
    # - O cuando RM rechazó (No Ok) Y release tiene contenido
    btn2_enabled = (
        bool(workflow.release and workflow.release.strip()) and  # Release debe tener contenido
        not (actividad_rm and actividad_rm.estado_proceso == 'Ok') and  # No debe estar ya aprobado
        (
            (actividad_scm1 and actividad_scm1.estado_proceso == 'Ok') or  # Línea base aprobada
            (actividad_rm and actividad_rm.estado_proceso == 'No Ok')  # O fue rechazado (re-solicitud)
        )
    )

    # Button 3: Solicitar Informe de diferencia
    # Debe estar deshabilitado cuando:
    # - Ya existe un informe de diferencia aprobado (estado_proceso='Ok')
    # Debe estar habilitado cuando:
    # - RM aprobó (Ok) Y no hay aprobación de Diff Info previa
    # - O cuando SCM rechazó Diff Info (No Ok)
    btn3_enabled = (
        not (actividad_scm2 and actividad_scm2.estado_proceso == 'Ok') and  # No debe estar ya aprobado
        (
            (actividad_rm and actividad_rm.estado_proceso == 'Ok') or  # RM aprobó
            (actividad_scm2 and actividad_scm2.estado_proceso == 'No Ok')  # O SCM rechazó (re-solicitud)
        )
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
        'fechas_form': FechasUpdateForm(instance=workflow),
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


@login_required
def workflow_detail_scm(request, id_workflow):
    """
    View workflow details for SCM role.
    Handles linea_base updates and SCM approval/rejection actions.
    """
    workflow = get_object_or_404(Workflow, id_workflow=id_workflow)

    # Verify user has SCM role
    if request.user.role != 'SCM':
        raise PermissionDenied("Solo usuarios con rol SCM pueden acceder a esta vista.")

    # Get process activities
    actividad_workflow = workflow.get_actividad_workflow()
    actividad_scm1 = workflow.get_actividad_scm1()
    actividad_scm2 = workflow.get_actividad_scm2()

    # Verify this workflow is in a state where SCM can act
    if not actividad_workflow or actividad_workflow.estado_workflow != 'Activo':
        raise PermissionDenied("Este workflow no está activo.")

    # Check which process is active
    proceso_activo = None
    if actividad_scm1 and actividad_scm1.estado_proceso == 'En Proceso':
        proceso_activo = 'linea base'
    elif actividad_scm2 and actividad_scm2.estado_proceso == 'En Proceso':
        proceso_activo = 'Diff Info'
    else:
        raise PermissionDenied("No hay actividades SCM pendientes para este workflow.")

    # Handle linea_base update
    if request.method == 'POST' and 'update_linea_base' in request.POST:
        if proceso_activo != 'linea base':
            messages.error(request, 'Solo se puede actualizar la línea base durante el proceso de línea base.')
            return redirect('workflow:workflow_detail_scm', id_workflow=id_workflow)

        linea_base_form = LineaBaseUpdateForm(request.POST, instance=workflow)
        if linea_base_form.is_valid():
            linea_base_form.save()
            messages.success(request, 'Línea base actualizada exitosamente.')
            return redirect('workflow:workflow_detail_scm', id_workflow=id_workflow)

    # Handle "Enviar Ok" button
    if request.method == 'POST' and 'enviar_ok' in request.POST:
        # Validación: Si el proceso es "linea base", verificar que el campo linea_base no esté vacío
        if proceso_activo == 'linea base':
            if not workflow.linea_base or not workflow.linea_base.strip():
                messages.error(request, 'No se puede aprobar la línea base si el campo está vacío. Por favor, ingrese la línea base primero.')
                return redirect('workflow:workflow_detail_scm', id_workflow=id_workflow)

        comentario = request.POST.get('comentario', '')

        # Get the next id_actividad
        max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
        next_id = (max_id or 0) + 1

        # Determine activity text based on proceso_activo
        if proceso_activo == 'linea base':
            actividad_text = 'Linea base aprobada'
        else:  # Diff Info
            actividad_text = 'Informe diferencias aprobado'

        # Create the approval activity
        Actividad.objects.create(
            workflow=workflow,
            id_actividad=next_id,
            usuario=request.user.username,
            estado_workflow='Activo',
            proceso=proceso_activo,
            estado_proceso='Ok',
            actividad=actividad_text,
            comentario=comentario if comentario else None
        )

        messages.success(request, f'{actividad_text} exitosamente.')
        return redirect('workflow:dashboard')

    # Handle "Enviar No Ok" button
    if request.method == 'POST' and 'enviar_no_ok' in request.POST:
        comentario = request.POST.get('comentario', '').strip()

        # Validación: El comentario es OBLIGATORIO para rechazar
        if not comentario:
            messages.error(request, 'El comentario es obligatorio para rechazar. Por favor, ingrese el motivo del rechazo.')
            return redirect('workflow:workflow_detail_scm', id_workflow=id_workflow)

        # Get the next id_actividad
        max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
        next_id = (max_id or 0) + 1

        # Determine activity text based on proceso_activo
        if proceso_activo == 'linea base':
            actividad_text = 'Linea base rechazada'
        else:  # Diff Info
            actividad_text = 'Informe diferencias rechazado'

        # Create the rejection activity
        Actividad.objects.create(
            workflow=workflow,
            id_actividad=next_id,
            usuario=request.user.username,
            estado_workflow='Activo',
            proceso=proceso_activo,
            estado_proceso='No Ok',
            actividad=actividad_text,
            comentario=comentario
        )

        messages.success(request, f'{actividad_text} exitosamente.')
        return redirect('workflow:dashboard')

    # Get all activities for display
    actividades = workflow.actividades.all()

    # Determine if linea_base can be edited
    # Only if proceso_activo is 'linea base'
    linea_base_editable = (proceso_activo == 'linea base')

    # Determine if "Enviar Ok" button should be enabled
    # For "linea base" process: only enable if linea_base field has content
    # For "Diff Info" process: always enable
    if proceso_activo == 'linea base':
        btn_ok_enabled = bool(workflow.linea_base and workflow.linea_base.strip())
    else:  # Diff Info
        btn_ok_enabled = True

    context = {
        'workflow': workflow,
        'actividades': actividades,
        'actividad_workflow': actividad_workflow,
        'actividad_scm1': actividad_scm1,
        'actividad_scm2': actividad_scm2,
        'proceso_activo': proceso_activo,
        'linea_base_editable': linea_base_editable,
        'linea_base_form': LineaBaseUpdateForm(instance=workflow),
        'btn_ok_enabled': btn_ok_enabled,
    }
    return render(request, 'workflow/workflow_detail_scm.html', context)


@login_required
def workflow_detail_rm(request, id_workflow):
    """
    View workflow details for Release Manager role.
    Handles codigo_rm updates and RM approval/rejection actions.
    """
    workflow = get_object_or_404(Workflow, id_workflow=id_workflow)

    # Verify user has Release Manager role
    if request.user.role != 'Release Manager':
        raise PermissionDenied("Solo usuarios con rol Release Manager pueden acceder a esta vista.")

    # Get process activities
    actividad_workflow = workflow.get_actividad_workflow()
    actividad_rm = workflow.get_actividad_rm()

    # Verify this workflow is in a state where RM can act
    if not actividad_workflow or actividad_workflow.estado_workflow != 'Activo':
        raise PermissionDenied("Este workflow no está activo.")

    # Verify RM Rev process is active
    if not actividad_rm or actividad_rm.estado_proceso != 'En Proceso':
        raise PermissionDenied("No hay revisión RM pendiente para este workflow.")

    # Initialize form variable
    codigo_rm_form = None

    # Handle codigo_rm update
    if request.method == 'POST' and 'update_codigo_rm' in request.POST:
        codigo_rm_form = CodigoRMUpdateForm(request.POST, instance=workflow)
        if codigo_rm_form.is_valid():
            codigo_rm_form.save()
            messages.success(request, 'Código RM actualizado exitosamente.')
            return redirect('workflow:workflow_detail_rm', id_workflow=id_workflow)
        else:
            # Form has errors, will be passed to template with error messages
            messages.error(request, 'Error al actualizar el código RM. Por favor, verifique los datos ingresados.')

    # Handle "Enviar Ok" button
    if request.method == 'POST' and 'enviar_ok' in request.POST:
        # Validation: codigo_rm must not be empty
        if not workflow.codigo_rm or not workflow.codigo_rm.strip():
            messages.error(request, 'No se puede aprobar la revisión RM si el código RM está vacío. Por favor, ingrese el código RM primero.')
            return redirect('workflow:workflow_detail_rm', id_workflow=id_workflow)

        comentario = request.POST.get('comentario', '')

        # Get the next id_actividad
        max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
        next_id = (max_id or 0) + 1

        # Create the approval activity
        Actividad.objects.create(
            workflow=workflow,
            id_actividad=next_id,
            usuario=request.user.username,
            estado_workflow='Activo',
            proceso='RM Rev',
            estado_proceso='Ok',
            actividad='Codigo RM enviado',
            comentario=comentario if comentario else None
        )

        messages.success(request, 'Código RM enviado exitosamente.')
        return redirect('workflow:dashboard')

    # Handle "Enviar No Ok" button
    if request.method == 'POST' and 'enviar_no_ok' in request.POST:
        comentario = request.POST.get('comentario', '').strip()

        # Validation: Comment is MANDATORY for rejection
        if not comentario:
            messages.error(request, 'El comentario es obligatorio para rechazar. Por favor, ingrese el motivo del rechazo.')
            return redirect('workflow:workflow_detail_rm', id_workflow=id_workflow)

        # Get the next id_actividad
        max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
        next_id = (max_id or 0) + 1

        # Create the rejection activity
        Actividad.objects.create(
            workflow=workflow,
            id_actividad=next_id,
            usuario=request.user.username,
            estado_workflow='Activo',
            proceso='RM Rev',
            estado_proceso='No Ok',
            actividad='Revision RM Rechazada',
            comentario=comentario
        )

        messages.success(request, 'Revisión RM rechazada exitosamente.')
        return redirect('workflow:dashboard')

    # Get all activities for display
    actividades = workflow.actividades.all()

    # Determine if "Enviar Ok" button should be enabled
    # Only enable if codigo_rm field has content
    btn_ok_enabled = bool(workflow.codigo_rm and workflow.codigo_rm.strip())

    # If form wasn't initialized (no POST for update_codigo_rm), create a fresh form
    if codigo_rm_form is None:
        codigo_rm_form = CodigoRMUpdateForm(instance=workflow)

    context = {
        'workflow': workflow,
        'actividades': actividades,
        'actividad_workflow': actividad_workflow,
        'actividad_rm': actividad_rm,
        'codigo_rm_form': codigo_rm_form,
        'btn_ok_enabled': btn_ok_enabled,
    }
    return render(request, 'workflow/workflow_detail_rm.html', context)
