<objective>
Corregir la lista detallada de actividades en el dashboard de Administrador para que muestre el historial COMPLETO de la tabla "actividades" en lugar de solo la actividad más reciente por workflow.

Las tarjetas de resumen y la matriz proceso/estado deben mantener su comportamiento actual (solo última actividad), pero la lista inferior y el CSV export deben mostrar toda la historia de actividades, incluyendo múltiples registros del mismo workflow.
</objective>

<context>
Archivo modificado anteriormente: `workflowup/workflow/views.py`
Template: `workflowup/workflow/templates/workflow/dashboard.html`

**Problema actual:**
La implementación actual usa `_get_workflows_with_latest_activity()` para todas las secciones, lo cual limita la lista detallada a mostrar solo una actividad por workflow. Esto es correcto para las tarjetas y la matriz, pero INCORRECTO para la lista detallada.

**Comportamiento requerido:**

1. **Tarjetas de resumen (Sección 1):**
   - ✅ MANTENER comportamiento actual
   - Usar solo la actividad más reciente por workflow
   - Calcular conteos basados en último estado

2. **Matriz proceso/estado (Sección 2):**
   - ✅ MANTENER comportamiento actual
   - Usar solo la actividad más reciente por workflow
   - Mostrar distribución del último estado de cada workflow

3. **Lista detallada (Sección 3):**
   - ❌ CAMBIAR comportamiento actual
   - Mostrar TODAS las actividades históricas
   - Incluir múltiples registros del mismo workflow
   - Aplicar filtros a toda la historia
   - Ejemplo: Si workflow #5 tiene 10 actividades, mostrar las 10 filas

4. **CSV Export:**
   - ❌ CAMBIAR comportamiento actual
   - Exportar TODAS las actividades filtradas
   - Incluir toda la historia, no solo últimas actividades
</context>

<requirements>

## Cambios en Backend (views.py)

### 1. Modificar función `_prepare_workflow_details(queryset)`

**Antes (incorrecto):**
```python
def _prepare_workflow_details(queryset):
    """Prepara los detalles de workflows para la tabla"""
    details = []
    for workflow in queryset:
        latest_activity = workflow.latest_activity
        if latest_activity:
            details.append({
                'id_workflow': workflow.id_workflow,
                # ... solo una actividad por workflow
            })
    return details
```

**Después (correcto):**
```python
def _prepare_workflow_details(workflows_queryset):
    """Prepara TODAS las actividades históricas con datos de workflow"""
    # Obtener IDs de workflows filtrados
    workflow_ids = workflows_queryset.values_list('id_workflow', flat=True)

    # Obtener TODAS las actividades de esos workflows
    all_activities = Actividad.objects.filter(
        workflow_id__in=workflow_ids
    ).select_related('workflow').order_by('-fecha')

    details = []
    for activity in all_activities:
        details.append({
            'id_workflow': activity.workflow.id_workflow,
            'nom_proyecto': activity.workflow.nom_proyecto,
            'componente': activity.workflow.componente or '',
            'id_proyecto': activity.workflow.id_proyecto,
            'estado_workflow': activity.estado_workflow,
            'proceso': activity.proceso or '',
            'estado_proceso': activity.estado_proceso or '',
            'usuario': activity.usuario,
            'fecha': activity.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            'comentario': activity.comentario or '',
        })
    return details
```

### 2. Modificar función `dashboard(request)`

La función debe:
- Seguir usando `_get_workflows_with_latest_activity()` para calcular estadísticas y matriz
- Usar la nueva `_prepare_workflow_details()` que retorna TODAS las actividades

**Verificar que:**
```python
# Para tarjetas y matriz: usar workflows con última actividad
workflows = _get_workflows_with_latest_activity()
workflows = _apply_admin_filters(workflows, request.GET)
stats = _calculate_workflow_stats(workflows)  # Solo últimas
matrix = _calculate_process_state_matrix(workflows)  # Solo últimas

# Para lista detallada: usar TODAS las actividades de workflows filtrados
workflow_details = _prepare_workflow_details(workflows)  # TODAS las actividades
```

### 3. Modificar función `dashboard_api(request)`

Similar a `dashboard()`, debe retornar:
- `stats` y `matrix` basados en últimas actividades
- `workflow_details` con TODAS las actividades históricas

### 4. Modificar función `export_workflows_csv(request)`

**Antes (incorrecto):**
Exporta solo últimas actividades

**Después (correcto):**
```python
def export_workflows_csv(request):
    """Exporta TODAS las actividades históricas filtradas a CSV"""
    if not request.user.is_authenticated or request.user.role != 'Administrador':
        return HttpResponseForbidden("No tiene permisos para acceder a esta página.")

    # Obtener workflows filtrados (para determinar cuáles incluir)
    workflows = _get_workflows_with_latest_activity()
    workflows = _apply_admin_filters(workflows, request.GET)

    # Obtener TODAS las actividades de esos workflows
    workflow_ids = workflows.values_list('id_workflow', flat=True)
    all_activities = Actividad.objects.filter(
        workflow_id__in=workflow_ids
    ).select_related('workflow').order_by('-fecha')

    # Crear CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    filename = f'workflows_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'ID Workflow', 'Proyecto', 'Componente', 'ID Proyecto',
        'Estado Workflow', 'Proceso', 'Estado Proceso', 'Usuario',
        'Fecha', 'Comentario'
    ])

    for activity in all_activities:
        writer.writerow([
            activity.workflow.id_workflow,
            activity.workflow.nom_proyecto,
            activity.workflow.componente or '',
            activity.workflow.id_proyecto,
            activity.estado_workflow,
            activity.proceso or '',
            activity.estado_proceso or '',
            activity.usuario,
            activity.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            activity.comentario or '',
        ])

    return response
```

## Cambios en Frontend (dashboard.html)

### Actualizar JavaScript `updateDashboard(data)`

La función debe manejar que `workflow_details` ahora contiene múltiples filas del mismo workflow:

```javascript
function updateDashboard(data) {
    // ... actualizar tarjetas (stats) ...
    // ... actualizar matriz (matrix) ...

    // Actualizar lista detallada (ahora con TODAS las actividades)
    const tbody = document.getElementById('workflow-table-body');
    tbody.innerHTML = '';

    if (data.workflow_details.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="px-6 py-4 text-center text-gray-500">No se encontraron registros</td></tr>';
    } else {
        data.workflow_details.forEach(item => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm">${item.id_workflow}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">${item.nom_proyecto}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">${item.componente}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">${item.id_proyecto}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs rounded-full ${getEstadoWorkflowClass(item.estado_workflow)}">
                        ${item.estado_workflow}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">${item.proceso}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs rounded-full ${getEstadoProcesoClass(item.estado_proceso)}">
                        ${item.estado_proceso}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">${item.usuario}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">${item.fecha}</td>
                <td class="px-6 py-4 text-sm">${item.comentario}</td>
            `;
            tbody.appendChild(row);
        });
    }

    // Actualizar contador de registros
    document.getElementById('workflow-count').textContent =
        `Mostrando ${data.workflow_details.length} registros (actividades históricas)`;
}
```

### Actualizar texto del contador

Cambiar el texto para aclarar que muestra actividades históricas:

```html
<p id="workflow-count" class="text-sm text-gray-600 mt-2">
    Mostrando {{ workflow_details|length }} registros (actividades históricas)
</p>
```

</requirements>

<validation>

## Pruebas de Verificación

### 1. Verificar Tarjetas (Sección 1)
- [ ] Las tarjetas muestran conteos correctos basados en última actividad
- [ ] Si un workflow tiene 5 actividades con estados diferentes, solo cuenta el último estado

### 2. Verificar Matriz (Sección 2)
- [ ] La matriz muestra distribución basada en última actividad
- [ ] Los conteos coinciden con el estado final de cada workflow

### 3. Verificar Lista Detallada (Sección 3)
- [ ] La lista muestra TODAS las actividades de TODOS los workflows
- [ ] Se ven múltiples filas del mismo id_workflow con fechas diferentes
- [ ] El contador muestra el total de actividades, no de workflows
- [ ] Ejemplo: Si hay 3 workflows con 5, 8, y 3 actividades respectivamente, debe mostrar 16 filas

### 4. Verificar Filtros
- [ ] Al filtrar por fecha, se aplica a workflow.created_at (para seleccionar workflows)
- [ ] Pero se muestran TODAS las actividades de los workflows seleccionados
- [ ] Al filtrar por usuario, se filtran workflows pero se muestran todas sus actividades
- [ ] Las tarjetas y matriz se recalculan correctamente con los workflows filtrados

### 5. Verificar CSV Export
- [ ] El CSV contiene TODAS las actividades históricas
- [ ] Incluye múltiples filas del mismo workflow
- [ ] El número de filas en CSV = número de filas en la tabla visible
- [ ] Los filtros aplicados se reflejan en el CSV

### 6. Comparación Manual
Para un workflow específico con múltiples actividades:
```python
# En Django shell
from workflow.models import Workflow, Actividad
wf = Workflow.objects.get(id_workflow=1)
activities = wf.actividades.all().order_by('-fecha')
print(f"Workflow {wf.id_workflow} tiene {activities.count()} actividades")
for a in activities:
    print(f"  - {a.fecha}: {a.estado_workflow} / {a.proceso} / {a.estado_proceso}")
```
- [ ] La lista en el dashboard muestra TODAS estas actividades
- [ ] Las tarjetas solo cuentan la más reciente

</validation>

<implementation_notes>

## Puntos Clave

1. **Separación de lógicas:**
   - Tarjetas + Matriz = Solo últimas actividades (ya implementado correctamente)
   - Lista + CSV = TODAS las actividades históricas (necesita corrección)

2. **Performance:**
   - Usar `select_related('workflow')` al obtener todas las actividades
   - Filtrar por `workflow_id__in` en lugar de loops
   - Ordenar por fecha descendente para mostrar más recientes primero

3. **Consistencia:**
   - Los filtros se aplican primero a workflows (basado en última actividad)
   - Luego se obtienen TODAS las actividades de esos workflows filtrados
   - Esto mantiene coherencia: las tarjetas/matriz muestran resumen de workflows filtrados, la lista muestra su historia completa

4. **Contadores:**
   - Actualizar texto para aclarar: "Mostrando X registros (actividades históricas)"
   - No confundir al usuario: X no es cantidad de workflows, sino de actividades

</implementation_notes>

<success_criteria>

El trabajo está completo cuando:

1. ✅ Las tarjetas muestran conteos basados en última actividad por workflow
2. ✅ La matriz muestra distribución basada en última actividad por workflow
3. ✅ La lista detallada muestra TODAS las actividades, incluyendo múltiples del mismo workflow
4. ✅ El CSV exporta TODAS las actividades visibles en la lista
5. ✅ Los filtros funcionan correctamente: filtran workflows pero muestran su historia completa
6. ✅ El contador indica "actividades históricas" para evitar confusión
7. ✅ No hay errores en consola ni en logs de Django
8. ✅ Las queries son eficientes (usar select_related, evitar N+1)

</success_criteria>
