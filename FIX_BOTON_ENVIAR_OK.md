# Corrección: Botón "Enviar Ok" en Vista SCM

## Problema Identificado

El botón "Enviar Ok" en la vista de "Detalle de Workflow" para el rol SCM estaba **siempre activo**, incluso cuando el campo `linea_base` estaba vacío o `null` en el proceso de "línea base".

## Comportamiento Esperado

**Para proceso "linea base":**
- ✓ Botón **DESHABILITADO** cuando `linea_base` es `null`, vacío o solo espacios
- ✓ Botón **HABILITADO** cuando `linea_base` tiene contenido válido

**Para proceso "Diff Info":**
- ✓ Botón **SIEMPRE HABILITADO** (no depende de `linea_base`)

## Archivos Modificados

### 1. `/workflowup/workflow/views.py`

#### Cambio 1: Agregar lógica para determinar estado del botón

**Ubicación:** Función `workflow_detail_scm()`, antes del `context = {...}`

**Código agregado:**
```python
# Determine if "Enviar Ok" button should be enabled
# For "linea base" process: only enable if linea_base field has content
# For "Diff Info" process: always enable
if proceso_activo == 'linea base':
    btn_ok_enabled = bool(workflow.linea_base and workflow.linea_base.strip())
else:  # Diff Info
    btn_ok_enabled = True
```

**Código en contexto:**
```python
context = {
    'workflow': workflow,
    'actividades': actividades,
    'actividad_workflow': actividad_workflow,
    'actividad_scm1': actividad_scm1,
    'actividad_scm2': actividad_scm2,
    'proceso_activo': proceso_activo,
    'linea_base_editable': linea_base_editable,
    'linea_base_form': LineaBaseUpdateForm(instance=workflow),
    'btn_ok_enabled': btn_ok_enabled,  # ← NUEVA LÍNEA
}
```

#### Cambio 2: Agregar validación backend

**Ubicación:** Función `workflow_detail_scm()`, en el handler de "Enviar Ok"

**Código agregado:**
```python
# Handle "Enviar Ok" button
if request.method == 'POST' and 'enviar_ok' in request.POST:
    # Validación: Si el proceso es "linea base", verificar que el campo linea_base no esté vacío
    if proceso_activo == 'linea base':
        if not workflow.linea_base or not workflow.linea_base.strip():
            messages.error(request, 'No se puede aprobar la línea base si el campo está vacío. Por favor, ingrese la línea base primero.')
            return redirect('workflow:workflow_detail_scm', id_workflow=id_workflow)

    # ... resto del código
```

**WHY:** Esta validación previene aprobaciones maliciosas o errores si alguien intenta enviar el formulario directamente sin pasar por el frontend.

---

### 2. `/workflowup/templates/workflow/workflow_detail_scm.html`

#### Cambio: Agregar atributo `disabled` condicional al botón

**Código anterior:**
```html
<button onclick="openApprovalModal()"
        class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded transition-colors duration-200">
    Enviar Ok
</button>
```

**Código corregido:**
```html
<button onclick="openApprovalModal()"
        {% if not btn_ok_enabled %}disabled{% endif %}
        class="{% if btn_ok_enabled %}bg-green-600 hover:bg-green-700{% else %}bg-gray-400 cursor-not-allowed{% endif %} text-white font-bold py-2 px-6 rounded transition-colors duration-200">
    Enviar Ok
</button>
```

**Cambios aplicados:**
1. ✓ Atributo `disabled` se agrega cuando `btn_ok_enabled` es `False`
2. ✓ Color cambia a gris (`bg-gray-400`) cuando está deshabilitado
3. ✓ Cursor cambia a `cursor-not-allowed` cuando está deshabilitado
4. ✓ Color verde interactivo cuando está habilitado

---

## Lógica de Validación

### Frontend (Template)

```django
{% if not btn_ok_enabled %}disabled{% endif %}
```

El botón se deshabilita visualmente en el navegador.

### Backend (Vista)

```python
if proceso_activo == 'linea base':
    btn_ok_enabled = bool(workflow.linea_base and workflow.linea_base.strip())
else:  # Diff Info
    btn_ok_enabled = True
```

La vista calcula si el botón debe estar habilitado basándose en el proceso activo y el contenido de `linea_base`.

### Backend (Validación adicional)

```python
if proceso_activo == 'linea base':
    if not workflow.linea_base or not workflow.linea_base.strip():
        messages.error(request, 'No se puede aprobar la línea base si el campo está vacío.')
        return redirect('workflow:workflow_detail_scm', id_workflow=id_workflow)
```

**Doble validación** para prevenir bypass del frontend.

---

## Tests de Validación

### Escenarios Probados

| # | Proceso | Línea Base | Botón Habilitado | Estado |
|---|---------|------------|------------------|--------|
| 1 | linea base | `null` | ❌ No | ✓ PASS |
| 2 | linea base | `''` (vacío) | ❌ No | ✓ PASS |
| 3 | linea base | `'   '` (espacios) | ❌ No | ✓ PASS |
| 4 | linea base | `'v1.0.0'` | ✅ Sí | ✓ PASS |
| 5 | Diff Info | `null` | ✅ Sí | ✓ PASS |
| 6 | Diff Info | `'v1.0.0'` | ✅ Sí | ✓ PASS |

**Resultado:** ✓ **TODOS LOS TESTS PASARON**

---

## Comportamiento Visual

### Botón Deshabilitado
```
┌─────────────────────────────┐
│      Enviar Ok              │  ← Gris, no clickeable
│  (bg-gray-400, disabled)    │     cursor: not-allowed
└─────────────────────────────┘
```

### Botón Habilitado
```
┌─────────────────────────────┐
│      Enviar Ok              │  ← Verde, hover interactivo
│  (bg-green-600, enabled)    │     cursor: pointer
└─────────────────────────────┘
```

---

## Flujo de Usuario SCM

### Escenario 1: Línea Base Vacía

1. Usuario SCM navega a detalle de workflow con proceso "linea base"
2. Campo `linea_base` está vacío
3. **Botón "Enviar Ok" aparece GRIS y DESHABILITADO**
4. Usuario debe ingresar línea base primero usando el formulario de edición
5. Al guardar la línea base, **el botón se habilita automáticamente** (la página se refresca)

### Escenario 2: Línea Base con Valor

1. Usuario SCM navega a detalle de workflow con proceso "linea base"
2. Campo `linea_base` tiene valor (ej: "v1.0.0")
3. **Botón "Enviar Ok" aparece VERDE y HABILITADO**
4. Usuario puede hacer clic para aprobar

### Escenario 3: Proceso Diff Info

1. Usuario SCM navega a detalle de workflow con proceso "Diff Info"
2. **Botón "Enviar Ok" aparece VERDE y HABILITADO** (sin importar línea base)
3. Usuario puede hacer clic para aprobar

---

## Seguridad

✓ **Validación Frontend:** El botón está deshabilitado en HTML
✓ **Validación Backend:** La vista valida antes de crear la actividad
✓ **Mensajes de Error:** El usuario recibe feedback claro si intenta aprobar sin línea base
✓ **Prevención de Bypass:** No se puede enviar el formulario directamente (POST)

---

## Checklist de Verificación

- [x] Lógica agregada en `views.py` para calcular `btn_ok_enabled`
- [x] Variable `btn_ok_enabled` pasada al contexto del template
- [x] Template actualizado con atributo `disabled` condicional
- [x] Estilos CSS actualizados (gris cuando deshabilitado)
- [x] Validación backend agregada en handler de "Enviar Ok"
- [x] Tests ejecutados y pasados (6/6)
- [x] Django check ejecutado sin errores
- [x] Documentación actualizada

---

## Notas Adicionales

### ¿Por qué verificar `strip()`?

```python
workflow.linea_base.strip()
```

Esto previene que un usuario ingrese solo espacios en blanco (ej: "   ") y el sistema lo considere como válido. La función `strip()` elimina espacios al inicio y final, y retorna una cadena vacía si solo hay espacios.

### ¿Por qué `bool()`?

```python
bool(workflow.linea_base and workflow.linea_base.strip())
```

La función `bool()` convierte el resultado a un booleano explícito:
- `None` → `False`
- `''` (vacío) → `False`
- `'   '` (solo espacios) → `False` (después de strip)
- `'v1.0.0'` → `True`

---

## Estado Final

✅ **CORRECCIÓN COMPLETADA Y VERIFICADA**

El botón "Enviar Ok" ahora funciona correctamente:
- Se deshabilita cuando `linea_base` está vacío (proceso "linea base")
- Se mantiene habilitado para proceso "Diff Info"
- Validación doble (frontend + backend) para máxima seguridad
- Feedback visual claro (color gris, cursor not-allowed)
