# SCM Quick Reference Card

## Login Credentials
- **Username:** `scm_user`
- **Password:** `test123`
- **Role:** SCM
- **Name:** María González

## URLs
- **SCM Dashboard:** `http://localhost:8000/workflow/`
- **Workflow Detail:** `http://localhost:8000/workflow/<id>/scm/`

## Key Files Modified/Created

### Created
1. `/workflowup/templates/workflow/dashboard_scm.html`
2. `/workflowup/templates/workflow/workflow_detail_scm.html`

### Modified
1. `/workflowup/workflow/forms.py` - Added `LineaBaseUpdateForm`
2. `/workflowup/workflow/views.py` - Added SCM routing + `workflow_detail_scm()` view
3. `/workflowup/workflow/urls.py` - Added SCM URL pattern

## Workflow States

### SCM Can Act When:
- Workflow `estado_workflow` = "Activo"
- AND one of:
  - `proceso='linea base'` AND `estado_proceso='En Proceso'`
  - `proceso='Diff Info'` AND `estado_proceso='En Proceso'`

### After SCM Approval (Ok):
- New activity created with `estado_proceso='Ok'`
- Workflow removed from SCM pending list
- Jefe de Proyecto can proceed to next step

### After SCM Rejection (No Ok):
- New activity created with `estado_proceso='No Ok'`
- Workflow removed from SCM pending list
- Jefe de Proyecto must re-request same process

## Actions Available

### 1. Update Línea Base (Only during "linea base" process)
- Edit the "Línea Base" field
- Click "Actualizar"
- Changes saved immediately

### 2. Approve (Enviar Ok)
- Click "Enviar Ok" button
- Enter optional comment (max 200 chars)
- Click "Confirmar Aprobación"
- Redirected to dashboard

### 3. Reject (Enviar No Ok)
- Click "Enviar No Ok" button
- Enter optional comment (max 200 chars)
- Click "Confirmar Rechazo"
- Redirected to dashboard

## Activity Texts Created

### For Línea Base Process:
- **Approval:** "Linea base aprobada"
- **Rejection:** "Linea base rechazada"

### For Diff Info Process:
- **Approval:** "Informe diferencias aprobado"
- **Rejection:** "Informe diferencias rechazado"

## Testing Flow

### Setup (as Jefe de Proyecto):
1. Login as `jproyecto`
2. Create workflow
3. Add release
4. Click "Solicitar Línea Base"

### Test Approval (as SCM):
1. Login as `scm_user`
2. Should see 1 workflow in list
3. Click "Revisar"
4. Update línea base: "baseline-v1.0.0"
5. Click "Actualizar"
6. Click "Enviar Ok"
7. Add comment: "Approved after review"
8. Click "Confirmar Aprobación"
9. Should redirect to dashboard
10. List should be empty

### Test Rejection (as SCM):
1. Login as `scm_user`
2. Click "Revisar" on pending workflow
3. Click "Enviar No Ok"
4. Add comment: "Please fix naming convention"
5. Click "Confirmar Rechazo"
6. Should redirect to dashboard

### Verify (as Jefe de Proyecto):
1. Login as `jproyecto`
2. Go to workflow detail
3. Check activity history
4. Verify status changed to Ok/No Ok
5. If Ok: "Solicitar Revisión RM" should be enabled
6. If No Ok: Can re-request línea base

## Common Issues

### "PermissionDenied" error
- **Cause:** Not logged in as SCM role
- **Solution:** Login with `scm_user` or another SCM role user

### Línea base field not editable
- **Cause:** Current process is not "linea base"
- **Normal:** Field only editable during línea base process

### Empty dashboard
- **Cause:** No workflows with SCM activities pending
- **Solution:** Create workflow as JP and request línea base

## Security Checks
- Role verification on all views
- CSRF protection on all forms
- Backend validation (not just JavaScript)
- Permission checks prevent unauthorized access

## Database Changes
- **NO migrations needed**
- Uses existing `Workflow.linea_base` field
- Uses existing `Actividad` model

## Code Location
- **Views:** `/workflowup/workflow/views.py` (lines 99-137, 376-493)
- **Forms:** `/workflowup/workflow/forms.py` (lines 116-133)
- **URLs:** `/workflowup/workflow/urls.py` (line 14)
- **Templates:** `/workflowup/templates/workflow/dashboard_scm.html`, `workflow_detail_scm.html`

## Support
For detailed information, see:
- `SCM_IMPLEMENTATION_GUIDE.md` - Full technical documentation
- `SCM_IMPLEMENTATION_SUMMARY.txt` - Implementation overview
- `test_scm_implementation.py` - Automated test suite
