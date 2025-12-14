<objective>
Implementar la funcionalidad completa para el rol "QA" en la aplicación WorkflowUp Django.

Esta implementación permitirá a los usuarios con rol QA:
- Visualizar workflows asignados a QA que están en proceso
- Gestionar planes de prueba asociados a cada workflow
- Aprobar o rechazar workflows basándose en resultados de pruebas
- Registrar actividades de aprobación/rechazo en el sistema de auditoría

Esta funcionalidad completa el flujo de trabajo secuencial: Jefe de Proyecto → SCM → Release Manager → QA.
</objective>

<context>
Proyecto: WorkflowUp - Sistema Django 5.2.8 con RBAC
Base de datos: MySQL 8.0
Rol objetivo: QA (Quality Assurance)

Arquitectura existente:
- Custom User model con 5 roles (Administrador, Jefe de Proyecto, SCM, Release Manager, QA)
- Sistema de workflows con proceso secuencial de aprobación
- Modelo Actividad para auditoría inmutable de estados
- Modelo PlanPruebaQA para gestión de pruebas

Patrones establecidos en la aplicación:
- Dashboard role-specific con templates separados (dashboard_jp.html, dashboard_scm.html, dashboard_rm.html)
- Vistas de detalle role-specific (workflow_detail.html, workflow_detail_scm.html, workflow_detail_rm.html)
- Actividades inmutables con id_actividad correlativo
- Estados de workflow: Nuevo, Activo, Cancelado, Cerrado
- Estados de proceso: No Iniciado, En Proceso, Ok, No Ok
- Procesos secuenciales: linea base → RM Rev → Diff Info → QA

Archivos relevantes:
@workflowup/workflow/models.py - Modelos Workflow, PlanPruebaQA, Actividad
@workflowup/workflow/views.py - Vistas existentes role-specific
@workflowup/workflow/forms.py - Formularios Django
@workflowup/workflow/urls.py - Routing de la app
@workflowup/workflow/templates/ - Templates HTML con Tailwind CSS
@CLAUDE.md - Convenciones del proyecto y arquitectura
</context>

<requirements>

## 1. Modificación del Modelo PlanPruebaQA

**Campo 'avance':**
- Cambiar de CharField a PositiveSmallIntegerField
- Rango válido: 0 a 100 (validar con MinValueValidator y MaxValueValidator)
- Valor por defecto: 0
- Representa porcentaje de avance

**Campo 'resultado':**
- Actualizar RESULTADO_CHOICES a:
  - 'No iniciado' (valor por defecto)
  - 'En proceso'
  - 'Aprobado'
  - 'No aprobado'

**IMPORTANTE:** Crear migración Django después de modificar el modelo.

## 2. Dashboard QA (Template y Vista)

**URL:** `/workflow` (misma URL, template diferente según rol)

**Template:** `dashboard_qa.html`

**Lógica de filtrado:**
Mostrar workflows que cumplan TODAS estas condiciones:
1. Estado workflow = 'Activo' (en la actividad más reciente del workflow)
2. Proceso = 'QA' (en la actividad más reciente del workflow)
3. Estado proceso = 'En Proceso' (en la actividad más reciente del workflow)

**Campos a mostrar en la tabla:**

Del modelo Workflow:
- id_workflow (ID Workflow)
- id_proyecto (ID Proyecto)
- jefe_proyecto (Jefe de Proyecto)
- nom_proyecto (Nombre Proyecto)
- creacion (Fecha Creación)
- qa_estimado (QA Estimado)
- pap_estimado (PAP Estimado)

De la actividad más reciente:
- estado_workflow (Estado Workflow)
- proceso (Proceso)
- actividad (Actividad)

**Botón de acción:**
- "Ver Detalle" → enlaza a vista detalle QA

**UI/UX:**
- Seguir el patrón de dashboard_scm.html y dashboard_rm.html
- Estilo Tailwind CSS consistente
- Tabla responsiva con headers claros
- Filtros opcionales por id_proyecto y rango de fechas (similar a dashboard JP)

## 3. Vista Detalle Workflow QA

**URL Pattern:** `/workflow/<int:id_workflow>/qa/`

**Restricción:** Solo accesible por usuarios con rol 'QA'

**Estructura de la vista:** 2 secciones (superior e inferior)

### Sección Superior: Información del Workflow (Read-only)

Mostrar TODOS los campos del modelo Workflow EXCEPTO id_workflow:
- id_proyecto
- nom_proyecto
- jefe_proyecto
- desc_proyecto
- componente
- linea_base
- codigo_rm
- release
- creacion
- qa_estimado
- pap_estimado

Todos los campos son NO EDITABLES (solo visualización).

### Sección Inferior: Plan de Pruebas QA (Editable)

**Tabla con todos los campos de PlanPruebaQA:**
- id_prueba (ID Prueba)
- prueba (Descripción de la Prueba)
- avance (mostrar header como "% Avance")
- resultado (Resultado)

**Ordenamiento:** Ascendente por id_prueba

**Acciones por fila:**

1. **Botón "Actualizar Avance"**
   - Modal/formulario inline para ingresar valor 0-100
   - Lógica automática al actualizar avance:
     - Si avance = 100 → resultado = 'Aprobado'
     - Si avance > 0 y < 100 → resultado = 'En proceso'
     - Si avance = 0 → resultado = 'No iniciado'
   - Implementación: AJAX para actualizar sin recargar página completa
   - Validación: Solo números enteros entre 0 y 100

2. **Botón "Rechazar/Reinyectar"**
   - Estado activo: Solo si avance < 100
   - Estado inactivo: Si avance = 100

   **Regla 1:** Si resultado = 'No iniciado' o 'En proceso'
   - Acción: Cambiar resultado a 'No aprobado'
   - Comentario: Opcional

   **Regla 2:** Si resultado = 'No aprobado'
   - Acción: Cambiar resultado a 'No iniciado' y avance a 0
   - Comentario: Opcional

   - Implementación: AJAX con confirmación
   - UI: Toggle behavior basado en estado actual

## 4. Botones de Aprobación/Rechazo del Workflow

### Botón "Enviar Ok"

**Condición de activación:**
- TODOS los items de PlanPruebaQA deben tener resultado = 'Aprobado'

**Flujo al hacer clic:**
1. Abrir modal de confirmación con:
   - Mensaje: "¿Confirma la aprobación del workflow?"
   - Campo comentario OPCIONAL (máximo 200 caracteres)
   - Botones: "Aceptar" y "Cancelar"

2. Si Cancelar → cerrar modal sin cambios

3. Si Aceptar → Crear nueva actividad:
   ```python
   # Calcular id_actividad correlativo
   max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
   next_id = (max_id or 0) + 1

   Actividad.objects.create(
       workflow=workflow,
       id_actividad=next_id,
       fecha=timezone.now(),  # Automático
       usuario=request.user.username,
       estado_workflow='Activo',
       proceso='QA',
       estado_proceso='Ok',
       actividad='Aprobado por QA',
       comentario=comentario_opcional  # Puede ser vacío
   )
   ```

4. Refrescar vista para mostrar cambios

### Botón "Enviar No Ok"

**Condición de activación:**
- AL MENOS UN item de PlanPruebaQA debe tener resultado = 'No aprobado'

**Flujo al hacer clic:**
1. Abrir modal de confirmación con:
   - Mensaje: "¿Confirma el rechazo del workflow?"
   - Campo comentario OBLIGATORIO (máximo 200 caracteres)
   - Validación: No permitir aceptar si comentario está vacío
   - Botones: "Aceptar" y "Cancelar"

2. Si Cancelar → cerrar modal sin cambios

3. Si Aceptar (solo si hay comentario) → Crear nueva actividad:
   ```python
   # Calcular id_actividad correlativo
   max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
   next_id = (max_id or 0) + 1

   Actividad.objects.create(
       workflow=workflow,
       id_actividad=next_id,
       fecha=timezone.now(),  # Automático
       usuario=request.user.username,
       estado_workflow='Activo',
       proceso='QA',
       estado_proceso='No Ok',
       actividad='Rechazado por QA',
       comentario=comentario_obligatorio  # Debe tener valor
   )
   ```

4. Refrescar vista para mostrar cambios

</requirements>

<implementation>

## Orden de implementación recomendado:

1. **Modificar modelo PlanPruebaQA** (workflowup/workflow/models.py)
   - Actualizar campo 'avance' a PositiveSmallIntegerField con validators
   - Actualizar RESULTADO_CHOICES
   - Crear y aplicar migración

2. **Crear formularios** (workflowup/workflow/forms.py)
   - AvanceUpdateForm: Para actualizar campo avance (validación 0-100)
   - Opcionalmente: Form para comentarios en modals

3. **Implementar vistas** (workflowup/workflow/views.py)
   - Actualizar vista dashboard() para manejar rol QA
   - Crear workflow_detail_qa() para detalle QA
   - Crear vistas AJAX para:
     - Actualizar avance
     - Toggle rechazar/reinyectar
     - Enviar Ok
     - Enviar No Ok

4. **Crear templates** (workflowup/workflow/templates/workflow/)
   - dashboard_qa.html
   - workflow_detail_qa.html
   - Modals para confirmaciones (pueden ser includes)

5. **Actualizar URLs** (workflowup/workflow/urls.py)
   - Agregar ruta para workflow_detail_qa
   - Agregar rutas para endpoints AJAX

6. **Testing manual**
   - Verificar filtrado de workflows en dashboard QA
   - Probar actualización de avance con lógica automática de resultado
   - Validar botón rechazar/reinyectar con ambas reglas
   - Confirmar que botones Ok/No Ok se activan correctamente
   - Verificar creación de actividades con campos correctos

## Patrones a seguir:

**Decoradores de vista:**
```python
@login_required
def workflow_detail_qa(request, id_workflow):
    # Verificar rol QA
    if request.user.role != 'QA':
        raise PermissionDenied
    # ...
```

**Creación de actividades (SIEMPRE con id correlativo):**
```python
from django.db.models import Max
from django.utils import timezone

max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
next_id = (max_id or 0) + 1

Actividad.objects.create(
    workflow=workflow,
    id_actividad=next_id,
    fecha=timezone.now(),
    usuario=request.user.username,
    # ... resto de campos
)
```

**Vistas AJAX (retornar JSON):**
```python
from django.http import JsonResponse

if request.method == 'POST':
    # Procesar
    return JsonResponse({'success': True, 'message': 'Actualizado'})
return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
```

**Templates Tailwind CSS:**
- Seguir estructura de dashboard_scm.html y dashboard_rm.html
- Usar clases de Tailwind existentes para consistencia
- Botones deshabilitados: `disabled` attribute + clases opacity-50 cursor-not-allowed

## Validaciones importantes:

1. **Modelo:** Validators en campo avance
   ```python
   from django.core.validators import MinValueValidator, MaxValueValidator

   avance = models.PositiveSmallIntegerField(
       default=0,
       validators=[MinValueValidator(0), MaxValueValidator(100)]
   )
   ```

2. **Vista:** Verificar permisos de rol QA antes de cualquier operación

3. **AJAX:** Validar datos en backend, no confiar solo en frontend

4. **Actividades:** NUNCA modificar actividades existentes, siempre crear nuevas

## NO hacer:

- NO modificar o eliminar actividades existentes (son inmutables)
- NO permitir acceso a usuarios sin rol QA
- NO olvidar el id_actividad correlativo (crítico para integridad)
- NO hardcodear valores, usar choices del modelo
- NO permitir comentarios > 200 caracteres
- NO permitir avance fuera del rango 0-100

</implementation>

<output>

Archivos a modificar/crear:

1. `./workflowup/workflow/models.py`
   - Modificar modelo PlanPruebaQA (campos avance y resultado)

2. `./workflowup/workflow/forms.py`
   - Agregar AvanceUpdateForm (si se necesita form tradicional como backup)

3. `./workflowup/workflow/views.py`
   - Actualizar dashboard() para rol QA
   - Crear workflow_detail_qa()
   - Crear vistas AJAX para todas las acciones

4. `./workflowup/workflow/urls.py`
   - Agregar rutas nuevas

5. `./workflowup/workflow/templates/workflow/dashboard_qa.html`
   - Nuevo template para dashboard QA

6. `./workflowup/workflow/templates/workflow/workflow_detail_qa.html`
   - Nuevo template para detalle workflow QA

7. Migración Django:
   - Crear con: `python workflowup/manage.py makemigrations`
   - Aplicar con: `python workflowup/manage.py migrate`

</output>

<verification>

Antes de declarar completa la implementación, verificar:

## Checklist de funcionalidad:

### Modelo y Base de datos
- [ ] Campo 'avance' es PositiveSmallIntegerField con rango 0-100
- [ ] Campo 'resultado' tiene las 4 opciones correctas
- [ ] Migración creada y aplicada sin errores
- [ ] Valores por defecto correctos (avance=0, resultado='No iniciado')

### Dashboard QA
- [ ] Solo muestra workflows con estado_workflow='Activo', proceso='QA', estado_proceso='En Proceso'
- [ ] Muestra todos los campos requeridos del workflow y actividad
- [ ] Botón "Ver Detalle" redirige correctamente
- [ ] Filtros funcionan correctamente
- [ ] Usuarios sin rol QA no pueden acceder

### Vista Detalle QA
- [ ] Sección superior muestra todos los campos del workflow (excepto id_workflow)
- [ ] Todos los campos superiores son read-only
- [ ] Tabla de plan de pruebas ordenada por id_prueba ascendente
- [ ] Header "% Avance" se muestra correctamente

### Actualización de Avance (AJAX)
- [ ] Acepta solo valores 0-100
- [ ] Lógica automática: avance=100 → resultado='Aprobado'
- [ ] Lógica automática: 0<avance<100 → resultado='En proceso'
- [ ] Lógica automática: avance=0 → resultado='No iniciado'
- [ ] Actualiza sin recargar página completa
- [ ] Muestra feedback visual de éxito/error

### Botón Rechazar/Reinyectar
- [ ] Solo activo si avance < 100
- [ ] Regla 1: 'No iniciado'/'En proceso' → 'No aprobado'
- [ ] Regla 2: 'No aprobado' → 'No iniciado' + avance=0
- [ ] Comentario es opcional en ambos casos
- [ ] Muestra confirmación antes de ejecutar

### Botón Enviar Ok
- [ ] Solo activo cuando TODOS los items tienen resultado='Aprobado'
- [ ] Modal muestra correctamente
- [ ] Comentario es opcional (máximo 200 caracteres)
- [ ] Cancelar cierra modal sin cambios
- [ ] Aceptar crea actividad con campos correctos:
  - [ ] id_actividad es correlativo
  - [ ] fecha es automática
  - [ ] usuario es username correcto
  - [ ] estado_workflow='Activo'
  - [ ] proceso='QA'
  - [ ] estado_proceso='Ok'
  - [ ] actividad='Aprobado por QA'
  - [ ] comentario se guarda (puede ser vacío)
- [ ] Vista se refresca mostrando cambios

### Botón Enviar No Ok
- [ ] Solo activo cuando AL MENOS UN item tiene resultado='No aprobado'
- [ ] Modal muestra correctamente
- [ ] Comentario es OBLIGATORIO (máximo 200 caracteres)
- [ ] No permite aceptar sin comentario
- [ ] Cancelar cierra modal sin cambios
- [ ] Aceptar crea actividad con campos correctos:
  - [ ] id_actividad es correlativo
  - [ ] fecha es automática
  - [ ] usuario es username correcto
  - [ ] estado_workflow='Activo'
  - [ ] proceso='QA'
  - [ ] estado_proceso='No Ok'
  - [ ] actividad='Rechazado por QA'
  - [ ] comentario se guarda (nunca vacío)
- [ ] Vista se refresca mostrando cambios

### Seguridad y Permisos
- [ ] Solo usuarios con rol 'QA' pueden acceder
- [ ] Usuarios sin autenticación redirigen a login
- [ ] Otros roles reciben PermissionDenied
- [ ] Validación en backend, no solo frontend

### UI/UX y Consistencia
- [ ] Estilo Tailwind consistente con otras vistas
- [ ] Mensajes de éxito/error claros
- [ ] Botones deshabilitados tienen estilo visual correcto
- [ ] Responsive design funciona correctamente
- [ ] Navegación coherente con resto de la app

</verification>

<success_criteria>

La implementación es exitosa cuando:

1. Usuario con rol QA puede ver dashboard filtrado con workflows asignados a QA
2. Usuario QA puede acceder a detalle de workflow y ver información completa
3. Usuario QA puede actualizar avance de pruebas y el resultado se actualiza automáticamente según las reglas
4. Botón rechazar/reinyectar funciona con ambas reglas correctamente
5. Botón "Enviar Ok" se activa solo cuando todas las pruebas están aprobadas y crea actividad correcta
6. Botón "Enviar No Ok" se activa cuando hay pruebas rechazadas, requiere comentario y crea actividad correcta
7. Todas las actividades se crean con id_actividad correlativo y campos correctos
8. La interfaz es consistente con el resto de la aplicación (Tailwind CSS)
9. Permisos y seguridad funcionan correctamente
10. No hay errores en consola del navegador ni en logs de Django

</success_criteria>

<testing_suggestions>

## Escenarios de prueba manual:

1. **Acceso básico:**
   - Login como usuario QA → debe ver dashboard QA
   - Login como otro rol → no debe ver dashboard QA

2. **Dashboard filtrado:**
   - Crear workflow en estado QA En Proceso → debe aparecer
   - Workflow en otro proceso → no debe aparecer
   - Workflow cerrado/cancelado → no debe aparecer

3. **Flujo completo de aprobación:**
   - Abrir workflow con 3 pruebas
   - Actualizar avance de prueba 1 a 50% → resultado debe ser 'En proceso'
   - Actualizar avance a 100% → resultado debe ser 'Aprobado'
   - Actualizar avance a 0% → resultado debe ser 'No iniciado'
   - Repetir para las 3 pruebas hasta 100%
   - Botón "Enviar Ok" debe activarse
   - Enviar Ok con comentario opcional
   - Verificar actividad creada en BD

4. **Flujo completo de rechazo:**
   - Abrir workflow con 2 pruebas aprobadas, 1 en proceso
   - En prueba 3: actualizar avance a 50%
   - Usar "Rechazar/Reinyectar" → debe cambiar a 'No aprobado'
   - Botón "Enviar No Ok" debe activarse
   - Enviar No Ok SIN comentario → debe mostrar error
   - Enviar No Ok CON comentario → debe crear actividad
   - Verificar actividad en BD

5. **Reinyección:**
   - Prueba con resultado 'No aprobado'
   - Clic en "Rechazar/Reinyectar" → debe volver a 'No iniciado' y avance=0
   - Verificar que se puede trabajar nuevamente en la prueba

6. **Edge cases:**
   - Intentar avance > 100 → debe rechazar
   - Intentar avance negativo → debe rechazar
   - Comentario > 200 caracteres → debe rechazar
   - Acceso directo a URL sin permisos → PermissionDenied

## Datos de prueba sugeridos:

Usar usuario qa_tester existente (password: test123)

Crear workflow de prueba:
- Estado: Activo
- Proceso QA en estado: En Proceso
- Con 3-5 items en PlanPruebaQA

</testing_suggestions>
