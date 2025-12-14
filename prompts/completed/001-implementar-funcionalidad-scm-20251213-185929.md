<objetivo>
Implementar la funcionalidad completa del rol "SCM" (Software Configuration Management) en la aplicación Django WorkflowUp existente.

El rol SCM tiene dos actividades principales:
1. **Agregar línea base**: Gestionar la línea base del proyecto
2. **Aprobar Informe de Diferencias**: Revisar y aprobar/rechazar informes de diferencias

Esta implementación debe integrarse perfectamente con la arquitectura existente, siguiendo los mismos patrones de diseño utilizados para el rol "Jefe de Proyecto" ya implementado.
</objetivo>

<contexto>
## Arquitectura del Proyecto

El proyecto WorkflowUp es una aplicación Django 5.2.8 con:
- **RBAC (Role-Based Access Control)** con 5 roles: Administrador, Jefe de Proyecto, SCM, Release Manager, QA
- **Custom User Model** en `users_admin.User`
- **MySQL 8.0** como base de datos
- **Tailwind CSS** (CDN) para estilos
- **manage.py** ubicado en `workflowup/manage.py` (no en la raíz)

## Modelos Existentes

Lee OBLIGATORIAMENTE estos archivos antes de comenzar:

@workflowup/workflow/models.py - Contiene:
- **Workflow**: Modelo principal con helper methods ya implementados
- **Actividad**: Log de actividades del workflow
- **PlanPruebaQA**: Plan de pruebas QA

Los helper methods del modelo Workflow son CRÍTICOS:
- `get_actividad_workflow()`: Última actividad general
- `get_actividad_scm1()`: Última actividad de "linea base"
- `get_actividad_scm2()`: Última actividad de "Diff Info"
- `get_actividad_rm()`: Última actividad de "RM Rev"
- `get_actividad_qa()`: Última actividad de "QA"

## Vistas Existentes de Referencia

@workflowup/workflow/views.py - Estudia el patrón implementado para "Jefe de Proyecto":
- Routing basado en roles en la función `dashboard()`
- Manejo de modales con JavaScript vanilla
- Creación de actividades con auto-incremento de `id_actividad`
- Uso de `django.db.models.Max` para obtener el siguiente ID

## Templates de Referencia

@workflowup/templates/workflow/dashboard_jp.html - Dashboard del Jefe de Proyecto
@workflowup/templates/workflow/workflow_detail.html - Vista de detalles con modales

**IMPORTANTE**: Los modales usan JavaScript vanilla puro y Tailwind CSS. Sigue EXACTAMENTE el mismo patrón.

## Convenciones del Proyecto

Lee @CLAUDE.md para las convenciones generales del proyecto.

**Reglas clave:**
- Usernames en minúsculas
- Soft delete con `is_active=False`
- Login redirect a `workflow:dashboard`
- Templates en `workflowup/templates/`
</contexto>

<definiciones_terminologia>
Las siguientes definiciones son CRÍTICAS y deben usarse consistentemente:

1. **"registro de actividad workflow"**: La actividad más reciente por fecha para un idWorkflow (usar `workflow.get_actividad_workflow()`)

2. **"registro de actividad scm-1"**: La actividad más reciente donde `proceso='linea base'` (usar `workflow.get_actividad_scm1()`)

3. **"registro de actividad scm-2"**: La actividad más reciente donde `proceso='Diff Info'` (usar `workflow.get_actividad_scm2()`)

4. **"registro de actividad RM"**: La actividad más reciente donde `proceso='RM Rev'` (usar `workflow.get_actividad_rm()`)

5. **"registro de actividad QA"**: La actividad más reciente donde `proceso='QA'` (usar `workflow.get_actividad_qa()`)

6. **"lista de actividades scm"**: QuerySet de workflows activos donde la actividad más reciente cumple:
   - (`proceso='linea base'` AND `estado_proceso='En Proceso'`) OR
   - (`proceso='Diff Info'` AND `estado_proceso='En Proceso'`)
</definiciones_terminologia>

<requerimientos>

## 1. Modificar la Vista Dashboard (workflowup/workflow/views.py)

**Objetivo**: Agregar routing para el rol SCM en la función `dashboard()` existente.

**Implementación**:
```python
@login_required
def dashboard(request):
    """
    Main workflow dashboard.
    Routes to different templates based on user role.
    """
    if request.user.role == 'Jefe de Proyecto':
        # Código existente para JP...
        return render(request, 'workflow/dashboard_jp.html', context)

    elif request.user.role == 'SCM':
        # NUEVA SECCIÓN: Implementar lógica para SCM aquí
        # Ver requerimientos detallados en sección 3 y 4
        pass

    # Default dashboard for other roles
    context = {'user': request.user}
    return render(request, 'workflow/dashboard.html', context)
```

**Validación de seguridad**: Verificar que `request.user.role == 'SCM'` antes de mostrar cualquier dato.

## 2. Crear Template dashboard_scm.html

**Ubicación**: `workflowup/templates/workflow/dashboard_scm.html`

**Estructura base**:
```django
{% extends "base_authenticated.html" %}

{% block title %}Workflow SCM - WorkflowUp{% endblock %}

{% block content %}
<!-- Implementar según requerimiento 4 -->
{% endblock %}
```

## 3. Generar "lista de actividades scm"

**Lógica en `views.py` para el bloque `elif request.user.role == 'SCM'`:**

```python
# Obtener todos los workflows activos
workflows = Workflow.objects.filter().prefetch_related('actividades')

# Filtrar workflows según "lista de actividades scm"
scm_workflows = []
for workflow in workflows:
    ultima_actividad = workflow.get_actividad_workflow()

    if ultima_actividad:
        # Verificar si el estado_workflow es "Activo"
        if ultima_actividad.estado_workflow == 'Activo':
            # Verificar las condiciones para SCM
            if (ultima_actividad.proceso == 'linea base' and
                ultima_actividad.estado_proceso == 'En Proceso'):
                scm_workflows.append(workflow)
            elif (ultima_actividad.proceso == 'Diff Info' and
                  ultima_actividad.estado_proceso == 'En Proceso'):
                scm_workflows.append(workflow)
```

**WHY**: Filtramos por estado "Activo" porque el SCM solo debe trabajar con workflows en progreso. Los workflows con estado "Cancelado" o "Cerrado" no requieren intervención SCM.

## 4. Vista Lista de Workflows SCM (dashboard_scm.html)

**Campos a mostrar en la tabla** (orden importante):

Desde el modelo **Workflow**:
1. `id_workflow` (ID Workflow)
2. `id_proyecto` (ID Proyecto)
3. `jefe_proyecto` (Jefe Proyecto) - username
4. `nom_proyecto` (Nombre Proyecto)
5. `creacion` (Creación) - formato: dd/mm/yyyy
6. `qa_estimado` (QA Estimado) - formato: dd/mm/yyyy
7. `pap_estimado` (PAP Estimado) - formato: dd/mm/yyyy

Desde la **última actividad** (registro de actividad workflow):
8. `estado_workflow` (Estado Workflow)
9. `proceso` (Proceso)
10. `actividad` (Actividad)

**Botón de acción**:
11. Botón "Ver Detalles" que enlace a la vista de detalles del workflow

**Diseño visual**: Seguir EXACTAMENTE el mismo patrón de tabla usado en `dashboard_jp.html` con clases Tailwind CSS idénticas.

## 5. Vista de Detalles del Workflow SCM

**Nueva función en views.py**: `workflow_detail_scm(request, id_workflow)`

### 5.1 Parte Superior - Información del Workflow

**Campos a mostrar** (todos NO EDITABLES excepto `linea_base`):

**Del modelo Workflow**:
- `id_workflow`, `id_proyecto`, `nom_proyecto`, `desc_proyecto`, `componente`
- `jefe_proyecto` (mostrar el nombre completo del usuario, no solo username)
- `creacion`, `qa_estimado`, `pap_estimado`
- `release` (solo lectura)
- `linea_base` - **EDITABLE** (ver 5.1.1)

**Campos calculados desde Actividad** (usando helper methods):
- **Estado Workflow**: `get_actividad_workflow().estado_workflow`
- **Línea Base**: `get_actividad_scm1().estado_proceso`
- **Revisión RM**: `get_actividad_rm().estado_proceso`
- **Diff Info**: `get_actividad_scm2().estado_proceso`
- **QA**: `get_actividad_qa().estado_proceso`

#### 5.1.1 Edición del campo lineaBase

**Patrón a seguir**: EXACTAMENTE igual a cómo se edita el campo `release` en `workflow_detail.html` líneas 46-56.

**Condición de editabilidad**:
```python
# En el context de la vista
linea_base_editable = (
    ultima_actividad and
    ultima_actividad.proceso == 'linea base' and
    ultima_actividad.estado_proceso == 'En Proceso'
)
```

**Implementación en template**:
```django
<div>
    <h3 class="text-sm font-medium text-gray-500">Línea Base</h3>
    {% if linea_base_editable %}
    <form method="post" class="flex items-center space-x-2">
        {% csrf_token %}
        <input type="hidden" name="update_linea_base" value="1">
        {{ linea_base_form.linea_base }}
        <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold py-1 px-3 rounded transition-colors duration-200">
            Actualizar
        </button>
    </form>
    {% else %}
    <p class="mt-1 text-lg text-gray-900">{{ workflow.linea_base|default:"-" }}</p>
    {% endif %}
</div>
```

**Form en views.py**:
```python
from django import forms

class LineaBaseUpdateForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = ['linea_base']
        widgets = {
            'linea_base': forms.TextInput(attrs={
                'class': 'rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'maxlength': '80',
            })
        }
```

**WHY**: Permitimos editar la línea base solo cuando el proceso está "En Proceso" porque es el momento en que el SCM debe ingresar o actualizar esta información antes de aprobar.

### 5.2 Parte Inferior - Historial de Actividades

**Tabla de actividades** mostrando todos los campos EXCEPTO `comentario`.

**Orden**: Más reciente primero (usar `.order_by('-fecha')` que ya es el default del modelo).

**Campos a mostrar**:
1. `id_actividad`
2. `fecha` (formato: dd/mm/yyyy HH:mm)
3. `usuario`
4. `estado_workflow`
5. `proceso`
6. `estado_proceso`
7. `actividad`
8. **Botón "Ver"** en la última columna (ver 5.2.1)

#### 5.2.1 Modal flotante para Comentario

**Patrón a seguir**: EXACTAMENTE igual al modal de comentarios en `workflow_detail.html` líneas 243-262.

**Implementación**:
```django
<td class="px-6 py-4 whitespace-nowrap text-sm">
    {% if actividad.comentario %}
    <button onclick="showComentario('{{ actividad.comentario|escapejs }}')"
            class="text-blue-600 hover:text-blue-900">Ver</button>
    {% else %}
    <span class="text-gray-400">-</span>
    {% endif %}
</td>
```

**JavaScript**: Copiar las funciones `showComentario()` y `closeComentarioModal()` del template de referencia.

## 6. Botones de Acción "Enviar Ok" y "Enviar No Ok"

**Ubicación**: En la vista de detalles del workflow SCM, después de la información del workflow y antes del historial.

**Comportamiento condicional**: Depende del valor de `proceso` en la última actividad.

### 6.1 Cuando proceso == "linea base"

#### Botón "Enviar Ok"

**Estado del botón**:
```python
# En la vista
btn_ok_enabled = (
    workflow.linea_base and
    workflow.linea_base.strip()  # No está vacío/null
)
```

**WHY**: El botón solo se activa cuando hay una línea base definida porque no tiene sentido aprobar algo que no existe.

**Al hacer clic**:
1. Abrir modal de confirmación
2. Permitir comentario **OPCIONAL** (max 200 caracteres)
3. Si usuario cancela → cerrar modal sin cambios
4. Si usuario acepta → crear nueva actividad:

```python
# Obtener siguiente id_actividad
max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
next_id = (max_id or 0) + 1

# Crear actividad
Actividad.objects.create(
    workflow=workflow,
    id_actividad=next_id,
    fecha=timezone.now(),  # auto_now_add lo hace automáticamente
    usuario=request.user.username,
    estado_workflow='Activo',
    proceso='linea base',
    estado_proceso='Ok',
    actividad='Linea base entregada',
    comentario=request.POST.get('comentario', '') or None
)
```

5. Refrescar la vista (redirect a la misma URL)

#### Botón "Enviar No Ok"

**Estado del botón**: Siempre activo (`btn_no_ok_enabled = True`)

**Al hacer clic**:
1. Abrir modal de confirmación
2. Comentario **OBLIGATORIO** (max 200 caracteres)
3. Validar que el comentario no esté vacío con JavaScript
4. Si usuario cancela → cerrar modal
5. Si usuario acepta → crear nueva actividad:

```python
# Validación en el backend
comentario = request.POST.get('comentario', '').strip()
if not comentario:
    messages.error(request, 'El comentario es obligatorio para rechazar.')
    return redirect('workflow:workflow_detail_scm', id_workflow=id_workflow)

# Crear actividad
Actividad.objects.create(
    workflow=workflow,
    id_actividad=next_id,
    usuario=request.user.username,
    estado_workflow='Activo',
    proceso='linea base',
    estado_proceso='No Ok',
    actividad='Linea base no disponible',
    comentario=comentario
)
```

6. Refrescar la vista

### 6.2 Cuando proceso == "Diff Info"

#### Botón "Enviar Ok"

**Estado del botón**: Siempre activo (`btn_ok_enabled = True`)

**Al hacer clic**:
1. Modal con comentario **OPCIONAL**
2. Si acepta, crear actividad:

```python
Actividad.objects.create(
    workflow=workflow,
    id_actividad=next_id,
    usuario=request.user.username,
    estado_workflow='Activo',
    proceso='Diff Info',
    estado_proceso='Ok',
    actividad='Informe de diferencias Ok',
    comentario=request.POST.get('comentario', '') or None
)
```

#### Botón "Enviar No Ok"

**Estado del botón**: Siempre activo

**Al hacer clic**:
1. Modal con comentario **OBLIGATORIO**
2. Validar comentario no vacío
3. Si acepta, crear actividad:

```python
Actividad.objects.create(
    workflow=workflow,
    id_actividad=next_id,
    usuario=request.user.username,
    estado_workflow='Activo',
    proceso='Diff Info',
    estado_proceso='No Ok',
    actividad='Conflictos en release presentes',
    comentario=comentario
)
```

### 6.3 Implementación de Modales

**Patrón a seguir**: Usar EXACTAMENTE el mismo patrón de modales que en `workflow_detail.html`.

**Diferencias clave**:
- El modal debe detectar si el comentario es obligatorio u opcional según el botón
- Validación JavaScript para comentario obligatorio

**Ejemplo de modal único que se adapta**:

```django
<!-- Modal SCM Actions -->
<div id="scmActionModal" class="hidden fixed z-10 inset-0 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
            <form method="post" id="scmActionForm">
                {% csrf_token %}
                <input type="hidden" name="scm_action" value="1">
                <input type="hidden" name="action_type" id="action_type">

                <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                    <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4" id="modal_title">
                        Confirmar Acción
                    </h3>
                    <div class="mt-2">
                        <label for="comentario" class="block text-sm font-medium text-gray-700 mb-2">
                            Comentario <span id="required_indicator" class="text-red-600"></span>
                            <span class="text-gray-500">(máximo 200 caracteres)</span>
                        </label>
                        <textarea name="comentario" id="comentario" rows="3" maxlength="200"
                                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                  placeholder="Ingrese un comentario..."></textarea>
                        <p id="comentario_error" class="mt-2 text-sm text-red-600 hidden">El comentario es obligatorio.</p>
                    </div>
                </div>
                <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                    <button type="submit"
                            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm">
                        Aceptar
                    </button>
                    <button type="button" onclick="closeScmModal()"
                            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
                        Cancelar
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
```

**JavaScript**:
```javascript
let comentarioObligatorio = false;

function openScmModal(actionType, isComentarioRequired) {
    document.getElementById('action_type').value = actionType;
    document.getElementById('comentario').value = '';
    document.getElementById('comentario_error').classList.add('hidden');

    comentarioObligatorio = isComentarioRequired;

    // Actualizar título y etiqueta según acción
    const titles = {
        'ok_linea_base': 'Aprobar Línea Base',
        'no_ok_linea_base': 'Rechazar Línea Base',
        'ok_diff_info': 'Aprobar Informe de Diferencias',
        'no_ok_diff_info': 'Rechazar Informe de Diferencias'
    };
    document.getElementById('modal_title').textContent = titles[actionType] || 'Confirmar Acción';

    // Mostrar/ocultar indicador de obligatorio
    if (isComentarioRequired) {
        document.getElementById('required_indicator').textContent = '(Obligatorio)';
    } else {
        document.getElementById('required_indicator').textContent = '(Opcional)';
    }

    document.getElementById('scmActionModal').classList.remove('hidden');
}

function closeScmModal() {
    document.getElementById('scmActionModal').classList.add('hidden');
}

// Validación antes de submit
document.getElementById('scmActionForm').addEventListener('submit', function(e) {
    if (comentarioObligatorio) {
        const comentario = document.getElementById('comentario').value.trim();
        if (!comentario) {
            e.preventDefault();
            document.getElementById('comentario_error').classList.remove('hidden');
            return false;
        }
    }
});
```

**Botones en el template**:
```django
<div class="border-t border-gray-200 pt-6 mt-6">
    <div class="flex flex-wrap gap-3">
        {% if ultima_actividad.proceso == 'linea base' %}
            <button onclick="openScmModal('ok_linea_base', false)"
                    {% if not btn_ok_enabled %}disabled{% endif %}
                    class="{% if btn_ok_enabled %}bg-green-600 hover:bg-green-700{% else %}bg-gray-400 cursor-not-allowed{% endif %} text-white font-bold py-2 px-4 rounded transition-colors duration-200">
                Enviar Ok
            </button>

            <button onclick="openScmModal('no_ok_linea_base', true)"
                    class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
                Enviar No Ok
            </button>

        {% elif ultima_actividad.proceso == 'Diff Info' %}
            <button onclick="openScmModal('ok_diff_info', false)"
                    class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
                Enviar Ok
            </button>

            <button onclick="openScmModal('no_ok_diff_info', true)"
                    class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200">
                Enviar No Ok
            </button>
        {% endif %}
    </div>
</div>
```

## 7. URLs y Routing

**Agregar en `workflowup/workflow/urls.py`**:

```python
from django.urls import path
from . import views

app_name = 'workflow'

urlpatterns = [
    # Existentes...
    path('', views.dashboard, name='dashboard'),

    # NUEVAS URLs para SCM
    path('scm/<int:id_workflow>/', views.workflow_detail_scm, name='workflow_detail_scm'),
]
```

**WHY**: Mantenemos todas las vistas SCM bajo la misma URL base `/workflow` como se solicitó, pero diferenciamos las vistas de detalle por rol.

</requerimientos>

<validaciones_seguridad>

1. **Verificar rol SCM**: En TODAS las vistas SCM, verificar `request.user.role == 'SCM'` antes de procesar.

2. **PermissionDenied**: Lanzar `raise PermissionDenied("Solo usuarios SCM pueden acceder a esta vista.")` si el rol no coincide.

3. **CSRF Protection**: Todos los formularios deben incluir `{% csrf_token %}`.

4. **Validación backend**: SIEMPRE validar en el backend, no solo en JavaScript:
   - Comentario obligatorio cuando corresponde
   - Existencia de la línea base antes de aprobar
   - Valores válidos para `action_type`

5. **SQL Injection**: Usar SIEMPRE el ORM de Django, nunca SQL crudo.

6. **XSS Prevention**: Usar `{{ variable|escapejs }}` en JavaScript y confiar en el auto-escape de Django templates.

</validaciones_seguridad>

<mejores_practicas_django>

1. **DRY (Don't Repeat Yourself)**: Reutilizar los helper methods del modelo `Workflow`.

2. **Fat Models, Thin Views**: La lógica de negocio debe estar en los modelos cuando sea posible.

3. **Use Django Messages**: Para feedback al usuario después de acciones:
   ```python
   from django.contrib import messages
   messages.success(request, 'Línea base aprobada exitosamente.')
   ```

4. **Atomic Transactions**: Para operaciones críticas, usar:
   ```python
   from django.db import transaction

   @transaction.atomic
   def crear_actividad_scm(request, workflow):
       # Operaciones que deben ser atómicas
   ```

5. **Prefetch Related**: Optimizar queries con `.prefetch_related('actividades')`.

6. **Template Inheritance**: Extender de `base_authenticated.html` consistentemente.

7. **Naming Conventions**:
   - Funciones de vista: `snake_case`
   - Clases: `PascalCase`
   - URLs: `kebab-case`

8. **Comments en Español**: Mantener consistencia con el resto del código del proyecto.

</mejores_practicas_django>

<verificacion>

Antes de declarar la implementación completa, verificar:

1. ✅ El dashboard SCM muestra correctamente la "lista de actividades scm"
2. ✅ El filtro por estado "Activo" y condiciones de proceso funciona
3. ✅ La vista de detalles muestra todos los campos requeridos
4. ✅ El campo `linea_base` solo es editable cuando `proceso='linea base'` y `estado_proceso='En Proceso'`
5. ✅ Los botones "Enviar Ok" y "Enviar No Ok" cambian su comportamiento según el proceso
6. ✅ El botón "Enviar Ok" para línea base solo se activa si `linea_base` no es null/vacío
7. ✅ Los comentarios obligatorios se validan en frontend Y backend
8. ✅ Las nuevas actividades se crean con el `id_actividad` correcto (auto-incremento)
9. ✅ Los modales siguen exactamente el mismo patrón que los existentes
10. ✅ La seguridad está implementada (verificación de rol SCM en todas las vistas)
11. ✅ Las URLs están correctamente configuradas
12. ✅ No hay errores de sintaxis Python o template Django
13. ✅ El diseño visual es consistente con el resto de la aplicación (mismo Tailwind CSS)

**Pruebas manuales recomendadas**:

```bash
# Activar entorno virtual
source py-env/bin/activate

# Ejecutar migraciones si se crearon
python workflowup/manage.py makemigrations
python workflowup/manage.py migrate

# Ejecutar servidor
python workflowup/manage.py runserver

# Probar con usuario SCM (crear uno si no existe)
python workflowup/manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> scm_user = User.objects.create_user(
...     username='scm_test',
...     email='scm@test.com',
...     password='test123',
...     role='SCM',
...     first_name='SCM',
...     last_name='Test'
... )
>>> scm_user.save()
```

**Navegación de prueba**:
1. Login con usuario SCM
2. Verificar que se muestra el dashboard SCM (no el default)
3. Verificar que solo aparecen workflows con las condiciones correctas
4. Click en "Ver Detalles" de un workflow
5. Probar edición de línea base (si aplica)
6. Probar botón "Enviar Ok" con comentario opcional
7. Probar botón "Enviar No Ok" con comentario obligatorio
8. Verificar que se crea la actividad correcta en la base de datos
9. Verificar que la vista se refresca correctamente

</verificacion>

<criterios_exito>

La implementación es exitosa cuando:

1. Un usuario con rol "SCM" ve el dashboard SCM al navegar a `/workflow`
2. El dashboard muestra solo los workflows que cumplen las condiciones de "lista de actividades scm"
3. La vista de detalles muestra toda la información requerida en las dos partes (superior e inferior)
4. El campo `linea_base` se puede editar solo en las condiciones especificadas
5. Los botones "Enviar Ok" y "Enviar No Ok" se comportan correctamente según el proceso actual
6. Las actividades se crean con todos los campos correctos
7. Los modales funcionan igual que en la vista del Jefe de Proyecto
8. No hay errores de permisos o seguridad
9. El diseño visual es consistente con el resto de la aplicación
10. Todo el código sigue las convenciones de Django y las buenas prácticas especificadas

</criterios_exito>

<notas_implementacion>

## Orden de implementación recomendado:

1. **Crear el formulario LineaBaseUpdateForm** en `workflowup/workflow/forms.py`
2. **Modificar la vista dashboard()** en `views.py` para agregar el routing SCM
3. **Crear la función workflow_detail_scm()** en `views.py`
4. **Crear el template dashboard_scm.html** (empezar con estructura básica)
5. **Crear el template workflow_detail_scm.html** (empezar con estructura básica)
6. **Implementar la lógica de "lista de actividades scm"** en dashboard()
7. **Completar el dashboard_scm.html** con la tabla de workflows
8. **Completar workflow_detail_scm.html** parte superior (información del workflow)
9. **Implementar la edición de línea base** (form + handler en vista)
10. **Completar workflow_detail_scm.html** parte inferior (historial de actividades)
11. **Implementar los modales** (HTML + JavaScript)
12. **Implementar los handlers de botones** "Enviar Ok" y "Enviar No Ok" en la vista
13. **Agregar las URLs** en `urls.py`
14. **Testing y ajustes finales**

## Posibles inconsistencias a preguntar:

Si encuentras alguna de estas situaciones, pregunta al usuario antes de continuar:

- ¿Qué pasa si un workflow no tiene ninguna actividad registrada? (aunque por el flujo actual siempre debería tener al menos una)
- ¿Debe haber paginación en el dashboard SCM si hay muchos workflows?
- ¿Qué pasa si el jefe_proyecto (username) no existe como usuario en el sistema?
- ¿Debe haber un botón para volver al dashboard desde la vista de detalles?

## Archivos que debes crear:

- `workflowup/templates/workflow/dashboard_scm.html` (nuevo)
- `workflowup/templates/workflow/workflow_detail_scm.html` (nuevo)

## Archivos que debes modificar:

- `workflowup/workflow/views.py` (agregar lógica SCM)
- `workflowup/workflow/forms.py` (agregar LineaBaseUpdateForm)
- `workflowup/workflow/urls.py` (agregar URL para workflow_detail_scm)

## NO modificar:

- `workflowup/workflow/models.py` (los modelos ya están completos)
- Templates de otros roles (dashboard_jp.html, workflow_detail.html)
- Configuración de settings.py

</notas_implementacion>
