# SCM Implementation Guide

## Overview

This document describes the complete implementation of the SCM (Software Configuration Management) role functionality in the WorkflowUp Django application.

## Implementation Date
December 13, 2025

## Files Created

### 1. Templates
- `/workflowup/templates/workflow/dashboard_scm.html` (5,538 bytes)
  - SCM dashboard showing workflows with pending SCM activities
  - Displays list of workflows requiring SCM action
  - Shows both "línea base" and "Diff Info" pending workflows

- `/workflowup/templates/workflow/workflow_detail_scm.html` (18,357 bytes)
  - SCM workflow detail view
  - Upper section: Workflow information with editable línea base field
  - Lower section: Activity history table
  - Two action modals: "Enviar Ok" and "Enviar No Ok"

## Files Modified

### 1. `/workflowup/workflow/forms.py`
**Added:**
- `LineaBaseUpdateForm` class
  - Form for updating the `linea_base` field of a workflow
  - Used exclusively by SCM role
  - Includes proper validation and Tailwind CSS styling

### 2. `/workflowup/workflow/views.py`
**Added:**
- Import for `LineaBaseUpdateForm`
- SCM routing in `dashboard()` function (lines 99-137)
  - Implements "lista de actividades scm" logic
  - Filters workflows where SCM has pending actions
  - Routes SCM users to `dashboard_scm.html`

- `workflow_detail_scm()` view function (lines 376-493)
  - Handles SCM workflow detail view
  - Permission check: Only SCM role can access
  - Handles línea base updates
  - Handles "Enviar Ok" (approval) button
  - Handles "Enviar No Ok" (rejection) button
  - Creates activities with proper auto-increment ID
  - Redirects to dashboard after actions

### 3. `/workflowup/workflow/urls.py`
**Added:**
- URL pattern for `workflow_detail_scm` view
  - Path: `<int:id_workflow>/scm/`
  - Name: `workflow_detail_scm`

## SCM Functionality Details

### Dashboard Logic ("lista de actividades scm")

The SCM dashboard displays workflows where the most recent activity meets one of these conditions:

1. `proceso='linea base'` AND `estado_proceso='En Proceso'` AND `estado_workflow='Activo'`
2. `proceso='Diff Info'` AND `estado_proceso='En Proceso'` AND `estado_workflow='Activo'`

**Implementation:**
```python
for workflow in all_workflows:
    ultima_actividad = workflow.get_actividad_workflow()
    if ultima_actividad and ultima_actividad.estado_workflow == 'Activo':
        actividad_scm1 = workflow.get_actividad_scm1()
        actividad_scm2 = workflow.get_actividad_scm2()

        if actividad_scm1 and actividad_scm1.estado_proceso == 'En Proceso':
            # Show in SCM dashboard - linea base pending
        elif actividad_scm2 and actividad_scm2.estado_proceso == 'En Proceso':
            # Show in SCM dashboard - Diff Info pending
```

### Workflow Detail View

#### Upper Section
Displays:
- Workflow information (ID, project, component, etc.)
- **Línea Base field**: Editable ONLY when `proceso_activo == 'linea base'`
  - Uses `LineaBaseUpdateForm`
  - Updates via POST with `update_linea_base` flag
- Current process indicator (shows which SCM activity is pending)
- Action buttons: "Enviar Ok" and "Enviar No Ok"

#### Lower Section
- Full activity history table
- Ordered by date (most recent first)
- Shows all activity fields with color-coded status badges
- Comentario display via modal

### Button Handlers

#### "Enviar Ok" Button
1. Opens modal with optional comentario field
2. On submit:
   - Creates new `Actividad` with auto-increment `id_actividad`
   - Sets `estado_proceso = 'Ok'`
   - Sets `actividad` text based on `proceso_activo`:
     - "Linea base aprobada" (if linea base)
     - "Informe diferencias aprobado" (if Diff Info)
   - Redirects to SCM dashboard

#### "Enviar No Ok" Button
1. Opens modal with optional comentario field
2. On submit:
   - Creates new `Actividad` with auto-increment `id_actividad`
   - Sets `estado_proceso = 'No Ok'`
   - Sets `actividad` text based on `proceso_activo`:
     - "Linea base rechazada" (if linea base)
     - "Informe diferencias rechazado" (if Diff Info)
   - Redirects to SCM dashboard

### Security & Validation

1. **Role Verification**: `workflow_detail_scm()` raises `PermissionDenied` if user role is not 'SCM'
2. **Workflow State Verification**: Only allows actions on workflows with `estado_workflow='Activo'`
3. **Process Verification**: Only allows actions when a valid SCM process is in "En Proceso" state
4. **CSRF Protection**: All forms include `{% csrf_token %}`
5. **Línea Base Edit Restriction**: Only editable during "linea base" process
6. **Backend Validation**: All form submissions validated on server side

## User Workflow

### As Jefe de Proyecto:
1. Create workflow
2. Add release
3. Request "línea base" (opens comentario modal)
4. System creates activity: `proceso='linea base'`, `estado_proceso='En Proceso'`

### As SCM:
1. Login with SCM role (e.g., `scm_user`)
2. Dashboard shows workflows with pending SCM activities
3. Click "Revisar" to open workflow detail
4. View workflow information
5. **For Línea Base process:**
   - Edit and update línea base field
   - Click "Enviar Ok" or "Enviar No Ok"
   - Add optional comentario
   - Confirm action
6. **For Diff Info process:**
   - Review information
   - Click "Enviar Ok" or "Enviar No Ok"
   - Add optional comentario
   - Confirm action
7. Redirected to dashboard
8. Workflow disappears from SCM pending list

### After SCM Action:
- **If Ok**: Jefe de Proyecto can proceed to next process
- **If No Ok**: Jefe de Proyecto must re-request the same process

## Testing

### Test User
- Username: `scm_user`
- Password: `test123` (if using default setup_users.py)
- Role: SCM
- Name: María González

### Test Workflow Available
- Workflow ID: 1
- Project: cambio de parametros de entrada
- Status: línea base pending

### Manual Testing Steps

1. **Login as Jefe de Proyecto** (e.g., `jproyecto`/`test123`)
   ```
   Navigate to: http://localhost:8000/workflow/
   Create a workflow
   Add release
   Click "Solicitar Línea Base"
   ```

2. **Login as SCM** (`scm_user`/`test123`)
   ```
   Navigate to: http://localhost:8000/workflow/
   Should see 1 workflow in the list
   Click "Revisar"
   ```

3. **Test Línea Base Update**
   ```
   Edit "Línea Base" field
   Click "Actualizar"
   Verify field was updated
   ```

4. **Test Approval**
   ```
   Click "Enviar Ok"
   Add optional comentario
   Click "Confirmar Aprobación"
   Verify redirected to dashboard
   Verify workflow disappeared from list
   ```

5. **Verify as Jefe de Proyecto**
   ```
   Login back as jproyecto
   Navigate to workflow detail
   Verify línea base status shows "Ok"
   Verify next button (Solicitar Revisión RM) is now enabled
   ```

### Automated Test
Run the included test script:
```bash
source py-env/bin/activate
python test_scm_implementation.py
```

Expected output: "ALL TESTS PASSED!"

## Architecture Patterns Followed

### 1. Role-Based Routing
- Similar to Jefe de Proyecto implementation
- Dashboard view routes based on `request.user.role`
- Separate templates per role

### 2. Helper Methods
- Uses existing `Workflow` model helper methods:
  - `get_actividad_workflow()`
  - `get_actividad_scm1()`
  - `get_actividad_scm2()`

### 3. Activity Creation Pattern
```python
# Get next ID
max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
next_id = (max_id or 0) + 1

# Create activity
Actividad.objects.create(
    workflow=workflow,
    id_actividad=next_id,
    usuario=request.user.username,
    estado_workflow='Activo',
    proceso=proceso_activo,
    estado_proceso='Ok',  # or 'No Ok'
    actividad=actividad_text,
    comentario=comentario if comentario else None
)
```

### 4. Template Inheritance
- Both templates extend `base_authenticated.html`
- Consistent styling with Tailwind CSS
- Vanilla JavaScript for modal handling (no jQuery)

### 5. Form Handling
- ModelForm pattern for `LineaBaseUpdateForm`
- POST with hidden field flags (`update_linea_base`, `enviar_ok`, `enviar_no_ok`)
- Redirect after POST to prevent duplicate submissions

## URL Structure

| URL Pattern | View | Template | Access |
|-------------|------|----------|--------|
| `/workflow/` | `dashboard()` | `dashboard_scm.html` | SCM role |
| `/workflow/<id>/scm/` | `workflow_detail_scm()` | `workflow_detail_scm.html` | SCM role |

## Database Impact

### No Schema Changes
- Implementation uses existing models
- No migrations required
- All fields already exist in `Workflow` and `Actividad` models

### Data Flow
1. Jefe de Proyecto creates activity: `proceso='linea base'`, `estado_proceso='En Proceso'`
2. SCM updates `workflow.linea_base` field
3. SCM creates activity: `proceso='linea base'`, `estado_proceso='Ok'` or `'No Ok'`

## Edge Cases Handled

1. **No workflows pending**: Dashboard shows empty state message
2. **Wrong role access**: `PermissionDenied` exception
3. **Inactive workflow**: View checks `estado_workflow='Activo'`
4. **No SCM activity pending**: View raises `PermissionDenied`
5. **Línea base edit during Diff Info**: Form only shown when `proceso_activo='linea base'`
6. **Empty comentario**: Stored as `None` (not empty string)

## Performance Considerations

1. **Prefetch Related**: Uses `prefetch_related('actividades')` to reduce queries
2. **Helper Methods**: Cached at model level
3. **Database Indexes**: Uses existing indexes on foreign keys and dates

## Future Enhancements

Potential improvements for future iterations:

1. **Email Notifications**: Notify Jefe de Proyecto when SCM approves/rejects
2. **Audit Trail**: Track all línea base changes
3. **Bulk Actions**: Allow SCM to process multiple workflows at once
4. **Filtering**: Add filters to SCM dashboard (by project, date, etc.)
5. **Comments History**: Show all comments for a specific process
6. **File Attachments**: Allow SCM to attach files to approvals/rejections

## Troubleshooting

### Dashboard shows empty even with pending workflows
- Check that workflows have `estado_workflow='Activo'`
- Verify activity has `estado_proceso='En Proceso'`
- Check user role is exactly 'SCM'

### Cannot edit línea base field
- Only editable when `proceso_activo='linea base'`
- Not editable during "Diff Info" process

### PermissionDenied error
- Verify user is logged in
- Check user role is 'SCM'
- Ensure workflow has valid SCM activity pending

### URL not found
- Verify URL is `/workflow/<id>/scm/` (note the `/scm/` suffix)
- Check URL routing in `urls.py`

## Conclusion

The SCM implementation is complete and fully functional. It follows all existing patterns in the codebase, provides proper security validation, and integrates seamlessly with the existing workflow process. All tests pass successfully, and the implementation is ready for production use.
