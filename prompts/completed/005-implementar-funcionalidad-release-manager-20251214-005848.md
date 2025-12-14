# Implementar Funcionalidad Release Manager en WorkflowUp

<objective>
Implementar funcionalidad completa para el rol "Release Manager" en la aplicación WorkflowUp, incluyendo modelo de datos, vistas específicas del rol, templates, y proceso de aprobación/rechazo de revisiones RM siguiendo las buenas prácticas de Django y los patrones arquitectónicos ya establecidos en el proyecto.

Esta funcionalidad permitirá a los Release Managers revisar workflows activos en proceso de revisión RM, asignar códigos RM, y aprobar o rechazar revisiones con seguimiento completo en el sistema de actividades.
</objective>

<context>
Este es un proyecto Django 5.2.8 existente con:
- Custom User model con RBAC (5 roles: Administrador, Jefe de Proyecto, SCM, Release Manager, QA)
- Sistema de workflows con proceso secuencial de aprobación
- Modelo Actividad para audit log inmutable
- Roles ya implementados: Jefe de Proyecto (vistas JP), SCM (vistas SCM)
- Proceso existente en Actividad.PROCESO_CHOICES: 'RM Rev' (Revisión RM)

**IMPORTANTE:**
- Revisa CLAUDE.md para entender la arquitectura completa del proyecto
- Sigue los patrones establecidos en las vistas de SCM (workflow/views.py) como referencia
- El campo proceso se llama 'RM Rev' (no 'Rev RM') según el código actual
- manage.py está en workflowup/manage.py (no en la raíz del proyecto)

Archivos clave a revisar:
- @workflowup/workflow/models.py - Modelos Workflow, Actividad, PlanPruebaQA
- @workflowup/workflow/views.py - Vistas existentes (dashboard, dashboard_scm como referencia)
- @workflowup/workflow/urls.py - URL routing
- @workflowup/templates/workflow/ - Templates existentes
</context>

<requirements>

## 1. Modelo de Datos

### 1.1 Ampliar modelo Workflow
Agregar campo `codigo_rm` al modelo Workflow:
- Tipo: CharField
- Longitud máxima: 9 caracteres
- Validación: Solo alfanuméricos (usar RegexValidator con patrón `^[a-zA-Z0-9]*$`)
- Nullable: True (blank=True, null=True)
- Verbose_name: 'Código RM'

### 1.2 Crear migración
Crear y aplicar migración para el nuevo campo:
```bash
python workflowup/manage.py makemigrations
python workflowup/manage.py migrate
```

## 2. Vista Dashboard Release Manager

### 2.1 Lógica de filtrado en views.py
Modificar la función `dashboard` en `workflowup/workflow/views.py`:
- Agregar condición para `request.user.role == 'Release Manager'`
- Filtrar workflows que cumplan TODAS estas condiciones:
  - Estado workflow 'Activo' (verificar en última actividad general)
  - Última actividad del proceso 'RM Rev' tenga estado_proceso = 'En Proceso'

Lógica específica:
```python
elif request.user.role == 'Release Manager':
    # Obtener todos los workflows
    all_workflows = Workflow.objects.all().prefetch_related('actividades')

    rm_workflows = []
    for workflow in all_workflows:
        # Verificar estado general del workflow
        ultima_actividad = workflow.get_actividad_workflow()
        if ultima_actividad and ultima_actividad.estado_workflow == 'Activo':
            # Verificar estado del proceso RM Rev
            actividad_rm = workflow.get_actividad_rm()
            if actividad_rm and actividad_rm.estado_proceso == 'En Proceso':
                rm_workflows.append(workflow)

    # Preparar datos para el template
    ...
```

### 2.2 Template dashboard_rm.html
Crear `workflowup/templates/workflow/dashboard_rm.html`:
- Extender de `base.html`
- Título: "Dashboard Release Manager"
- Tabla con los siguientes campos del modelo Workflow:
  - id_workflow (ID Workflow)
  - id_proyecto (ID Proyecto)
  - jefe_proyecto (Jefe de Proyecto)
  - nom_proyecto (Nombre Proyecto)
  - creacion (Fecha Creación)
  - qa_estimado (QA Estimado)
  - pap_estimado (PAP Estimado)
- Campos adicionales de la última actividad:
  - estado_workflow (Estado Workflow)
  - proceso (Proceso)
  - actividad (Actividad)
- Botón "Ver Detalle" que enlaza a `workflow:workflow_detail_rm` con id_workflow

Usar clases de Tailwind CSS consistentes con dashboard_scm.html y dashboard_jp.html existentes.

## 3. Vista de Detalle Release Manager

### 3.1 Crear vista workflow_detail_rm en views.py
Características:
- Decorador: `@login_required`
- Verificar que user.role == 'Release Manager', sino PermissionDenied
- Recibir parámetro id_workflow
- Obtener workflow con get_object_or_404

Funcionalidad:
1. **Formulario de actualización de código_rm:**
   - Crear form CodigoRMUpdateForm en forms.py con validación alfanumérica
   - Manejar POST con 'update_codigo_rm'

2. **Botón "Enviar Ok":**
   - Verificar que codigo_rm no sea null ni vacío (habilitar/deshabilitar en template)
   - Crear nueva actividad con:
     - id_actividad: correlativo automático (Max + 1)
     - fecha: auto_now_add=True
     - usuario: request.user.username
     - estado_workflow: 'Activo'
     - proceso: 'RM Rev'
     - estado_proceso: 'Ok'
     - actividad: 'Codigo RM enviado'
     - comentario: opcional (hasta 200 caracteres)
   - Redirect a la misma vista (permanece en detalle)

3. **Botón "Enviar No Ok":**
   - Siempre habilitado
   - Comentario OBLIGATORIO (validar antes de crear actividad)
   - Crear nueva actividad con:
     - id_actividad: correlativo automático
     - fecha: auto_now_add
     - usuario: request.user.username
     - estado_workflow: 'Activo'
     - proceso: 'RM Rev'
     - estado_proceso: 'No Ok'
     - actividad: 'Revision RM Rechazada'
     - comentario: requerido
   - Redirect a la misma vista

### 3.2 Template workflow_detail_rm.html
Estructura en 2 partes:

**Parte Superior - Información del Workflow:**
- Mostrar TODOS los campos del modelo Workflow (no editables)
- EXCEPCIÓN: campo codigo_rm editable mediante formulario inline
- Campos a mostrar:
  - id_workflow, id_proyecto, nom_proyecto, jefe_proyecto
  - desc_proyecto, componente
  - linea_base, codigo_rm (EDITABLE), release
  - creacion, qa_estimado, pap_estimado
- Botón "Actualizar Código RM" para guardar cambios en codigo_rm

**Parte Inferior - Historial de Actividades:**
- Tabla con todas las actividades del workflow (orden descendente por fecha)
- Columnas: id_actividad, fecha, usuario, estado_workflow, proceso, estado_proceso, actividad
- Última columna: Botón "Ver Comentario"
  - Abre modal/ventana flotante con el contenido del comentario
  - Si comentario es null/vacío, mostrar "Sin comentario"

**Botones de Acción:**
- Botón "Enviar Ok":
  - Deshabilitado si codigo_rm es null o vacío
  - Al hacer clic: modal de confirmación con textarea opcional para comentario (max 200 chars)
  - Opciones: "Cancelar" (cierra modal) o "Aceptar" (ejecuta acción)

- Botón "Enviar No Ok":
  - Siempre habilitado
  - Al hacer clic: modal de confirmación con textarea OBLIGATORIO para comentario (max 200 chars)
  - Validar que comentario no esté vacío antes de permitir "Aceptar"
  - Opciones: "Cancelar" o "Aceptar"

Usar Tailwind CSS y JavaScript para modales. Referencia el patrón de workflow_detail_scm.html.

## 4. Actualizar Vistas Existentes

### 4.1 Vista workflow_detail (Jefe de Proyecto)
En `workflowup/templates/workflow/workflow_detail.html`:
- Agregar campo codigo_rm (solo lectura) en la sección de información del workflow
- Posición: después de linea_base, antes de release (consistente con vista RM)
- Formato: "Código RM: {{ workflow.codigo_rm|default:'No asignado' }}"

### 4.2 Vista workflow_detail_scm (SCM)
En `workflowup/templates/workflow/workflow_detail_scm.html`:
- Agregar campo codigo_rm (solo lectura) en la sección de información del workflow
- Posición: después de linea_base, antes de release
- Formato: "Código RM: {{ workflow.codigo_rm|default:'No asignado' }}"

## 5. URLs

### 5.1 Agregar ruta en workflow/urls.py
```python
path('<int:id_workflow>/rm/', views.workflow_detail_rm, name='workflow_detail_rm'),
```

Nota: Aunque la vista se accede desde /workflow/, la URL específica de detalle es /workflow/<id>/rm/ siguiendo el patrón consistente con SCM.

## 6. Forms

### 6.1 Crear CodigoRMUpdateForm en workflow/forms.py
```python
class CodigoRMUpdateForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = ['codigo_rm']
        widgets = {
            'codigo_rm': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm...',
                'maxlength': '9',
                'placeholder': 'Ej: RM123456A'
            })
        }

    def clean_codigo_rm(self):
        codigo = self.cleaned_data.get('codigo_rm')
        if codigo:
            # Validar solo alfanuméricos
            import re
            if not re.match(r'^[a-zA-Z0-9]+$', codigo):
                raise forms.ValidationError('El código RM solo puede contener letras y números')
        return codigo
```

</requirements>

<implementation>

## Secuencia de Implementación

Sigue estos pasos EN ORDEN para evitar errores:

1. **Modelo y Migración:**
   - Modificar workflowup/workflow/models.py
   - Ejecutar makemigrations y migrate
   - Verificar que la migración se aplique correctamente

2. **Forms:**
   - Crear CodigoRMUpdateForm en workflowup/workflow/forms.py

3. **Views:**
   - Modificar dashboard() para agregar lógica Release Manager
   - Crear workflow_detail_rm() siguiendo patrón de workflow_detail_scm()
   - Importar el nuevo formulario

4. **URLs:**
   - Agregar ruta workflow_detail_rm en workflowup/workflow/urls.py

5. **Templates:**
   - Crear dashboard_rm.html basado en dashboard_scm.html
   - Crear workflow_detail_rm.html basado en workflow_detail_scm.html
   - Actualizar workflow_detail.html (agregar codigo_rm readonly)
   - Actualizar workflow_detail_scm.html (agregar codigo_rm readonly)

6. **Testing Manual:**
   - Verificar que el dashboard RM muestra workflows correctos
   - Probar edición de codigo_rm
   - Probar aprobación con código RM presente
   - Probar rechazo con comentario obligatorio
   - Verificar que las actividades se registran correctamente

## Patrones a Seguir

### Creación de Actividades (CRÍTICO)
Siempre usar este patrón para crear actividades:
```python
from django.db.models import Max

# Obtener próximo id_actividad
max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
next_id = (max_id or 0) + 1

# Crear actividad
Actividad.objects.create(
    workflow=workflow,
    id_actividad=next_id,
    usuario=request.user.username,
    estado_workflow='Activo',
    proceso='RM Rev',
    estado_proceso='Ok',  # o 'No Ok'
    actividad='Codigo RM enviado',  # o 'Revision RM Rechazada'
    comentario=comentario if comentario else None
)
```

### Validación de Código RM
El botón "Enviar Ok" se habilita solo si:
```python
# En el context de la vista
btn_enviar_ok_enabled = bool(workflow.codigo_rm and workflow.codigo_rm.strip())
```

En el template:
```html
<button
    {% if not btn_enviar_ok_enabled %}disabled{% endif %}
    class="..."
    onclick="mostrarModalOk()">
    Enviar Ok
</button>
```

### Modal de Confirmación con JavaScript
Usar JavaScript vanilla o Alpine.js (si está disponible) para los modales:
- Modal debe tener backdrop oscuro
- Textarea para comentario con contador de caracteres (max 200)
- Para "No Ok": validar comentario no vacío antes de permitir submit
- Form action debe ser POST con CSRF token

</implementation>

<constraints>

## Lo que NO debes hacer (y por qué)

1. **No modificar actividades existentes** - Las actividades son inmutables (audit log). Siempre crear nuevas actividades.

2. **No usar 'Rev RM'** - El proceso se llama 'RM Rev' según el código existente en Actividad.PROCESO_CHOICES.

3. **No permitir "Enviar Ok" sin código RM** - El código RM es requisito obligatorio para aprobar. Esto previene aprobaciones incompletas.

4. **No permitir "Enviar No Ok" sin comentario** - Los rechazos requieren justificación para trazabilidad. El sistema debe validar esto antes de crear la actividad.

5. **No usar rutas absolutas en templates** - Usar siempre {% url 'namespace:name' %} para mantener flexibilidad.

6. **No duplicar código** - Reutilizar patrones de dashboard_scm.html y workflow_detail_scm.html.

7. **No olvidar prefetch_related** - Siempre usar .prefetch_related('actividades') al consultar workflows para optimizar queries.

</constraints>

<output>

Archivos a crear/modificar:

1. **Modelo:** `workflowup/workflow/models.py`
   - Agregar campo codigo_rm a clase Workflow
   - Incluir RegexValidator para validación alfanumérica

2. **Migración:** Generar y aplicar automáticamente
   ```bash
   python workflowup/manage.py makemigrations workflow
   python workflowup/manage.py migrate
   ```

3. **Forms:** `workflowup/workflow/forms.py`
   - Crear CodigoRMUpdateForm

4. **Views:** `workflowup/workflow/views.py`
   - Modificar función dashboard() - agregar elif para Release Manager
   - Crear función workflow_detail_rm()

5. **URLs:** `workflowup/workflow/urls.py`
   - Agregar path para workflow_detail_rm

6. **Templates:**
   - Crear: `workflowup/templates/workflow/dashboard_rm.html`
   - Crear: `workflowup/templates/workflow/workflow_detail_rm.html`
   - Modificar: `workflowup/templates/workflow/workflow_detail.html` (agregar codigo_rm readonly)
   - Modificar: `workflowup/templates/workflow/workflow_detail_scm.html` (agregar codigo_rm readonly)

</output>

<verification>

Antes de declarar la tarea completa, verifica:

1. **Migración exitosa:**
   ```bash
   python workflowup/manage.py showmigrations workflow
   ```
   Debe mostrar la nueva migración aplicada (marcada con [X])

2. **Dashboard RM funcional:**
   - Login como usuario con rol 'Release Manager'
   - Acceder a /workflow/
   - Verificar que muestra solo workflows Activos con RM Rev En Proceso
   - Confirmar que todos los campos requeridos se muestran

3. **Detalle RM funcional:**
   - Click en "Ver Detalle" desde dashboard RM
   - Verificar que todos los campos del workflow se muestran
   - Editar codigo_rm y guardar (debe aceptar solo alfanuméricos)
   - Verificar que botón "Enviar Ok" está deshabilitado sin código RM
   - Agregar código RM y verificar que botón se habilita

4. **Aprobación RM:**
   - Con código RM presente, click en "Enviar Ok"
   - Agregar comentario opcional
   - Aceptar y verificar que:
     - Nueva actividad creada con estado_proceso='Ok'
     - actividad='Codigo RM enviado'
     - Vista se actualiza correctamente

5. **Rechazo RM:**
   - Click en "Enviar No Ok"
   - Intentar aceptar sin comentario (debe fallar/avisar)
   - Agregar comentario y aceptar
   - Verificar que:
     - Nueva actividad creada con estado_proceso='No Ok'
     - actividad='Revision RM Rechazada'
     - Comentario se guardó correctamente

6. **Vistas actualizadas:**
   - Login como Jefe de Proyecto
   - Verificar que workflow_detail.html muestra codigo_rm (readonly)
   - Login como SCM
   - Verificar que workflow_detail_scm.html muestra codigo_rm (readonly)

7. **Consistencia UI:**
   - Todos los templates usan Tailwind CSS consistentemente
   - Modales funcionan correctamente
   - Botones y formularios tienen estilos coherentes

</verification>

<success_criteria>

La implementación es exitosa cuando:

✓ Campo codigo_rm agregado al modelo Workflow con validación alfanumérica
✓ Migración aplicada sin errores
✓ Dashboard RM muestra workflows correctos (Activos + RM Rev En Proceso)
✓ Vista de detalle RM permite editar codigo_rm
✓ Botón "Enviar Ok" se habilita/deshabilita según código RM
✓ Botón "Enviar No Ok" valida comentario obligatorio
✓ Actividades se crean correctamente con todos los campos requeridos
✓ Vistas de Jefe de Proyecto y SCM muestran codigo_rm (readonly)
✓ UI consistente con el resto de la aplicación
✓ No hay errores en consola del navegador o logs de Django
✓ Todas las verificaciones del checklist pasan

</success_criteria>

<notes>

**Para el desarrollador:**

Este es un proyecto académico (proyecto de título) en producción activa. Sigue rigurosamente:
- Los patrones establecidos en las vistas SCM existentes
- Las buenas prácticas de Django documentadas en CLAUDE.md
- La inmutabilidad del modelo Actividad
- La validación de datos antes de crear actividades

Si encuentras inconsistencias o indefiniciones en los requerimientos, pregunta antes de proceder. Es mejor aclarar que implementar incorrectamente.

Referencia los archivos existentes, especialmente:
- workflow_detail_scm() como patrón para workflow_detail_rm()
- dashboard_scm.html como patrón para dashboard_rm.html
- La lógica de botones en workflow_detail.html para el Jefe de Proyecto

</notes>
