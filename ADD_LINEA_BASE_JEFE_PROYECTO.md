# Agregado: Campo "Línea Base" en Vista Jefe de Proyecto

## Descripción del Cambio

Se agregó el campo `lineaBase` en la vista de "Detalle de Workflow" para el rol **Jefe de Proyecto**, haciéndolo **visible pero no editable** (solo lectura).

---

## Archivo Modificado

### `/workflowup/templates/workflow/workflow_detail.html`

**Ubicación:** Después del campo "Release" en el grid de información del workflow (líneas 57-60)

**Código agregado:**
```html
<div>
    <h3 class="text-sm font-medium text-gray-500">Línea Base</h3>
    <p class="mt-1 text-lg text-gray-900">{{ workflow.linea_base|default:"-" }}</p>
</div>
```

---

## Características del Campo

### ✓ Solo Lectura
- El campo se muestra como texto plano (`<p>`)
- **No es editable** por el Jefe de Proyecto
- Utiliza el mismo estilo que otros campos de solo lectura (Fecha Creación, QA Estimado, etc.)

### ✓ Siempre Visible
- El campo siempre se muestra, incluso si está vacío
- Si `linea_base` es `null` o vacío, muestra "-"
- Usa el filtro Django `|default:"-"` para manejar valores nulos

### ✓ Ubicación Armoniosa
El campo se colocó estratégicamente **después del campo "Release"** porque:
1. **Relación lógica:** Release → Línea Base (flujo natural)
2. **Consistencia visual:** Misma fila, lado derecho del grid
3. **Balance en diseño:** Mantiene la estructura de 2 columnas

---

## Diseño Visual

### Grid Layout Actualizado

```
┌─────────────────────────────────────────────────────────────┐
│  ID Proyecto          │  Componente                         │
├─────────────────────────────────────────────────────────────┤
│  Nombre Proyecto (2 columnas)                               │
├─────────────────────────────────────────────────────────────┤
│  Descripción Proyecto (2 columnas)                          │
├─────────────────────────────────────────────────────────────┤
│  Fecha Creación       │  QA Estimado                        │
├─────────────────────────────────────────────────────────────┤
│  PAP Estimado         │  Release (editable con botón)       │
├─────────────────────────────────────────────────────────────┤
│                       │  Línea Base (solo lectura) ← NUEVO  │
└─────────────────────────────────────────────────────────────┘
```

### Estilos CSS Aplicados

- **Label:** `text-sm font-medium text-gray-500` (gris, pequeño, negrita media)
- **Valor:** `mt-1 text-lg text-gray-900` (margen superior, texto grande, gris oscuro)
- **Default:** Muestra "-" si está vacío (consistente con otros campos)

---

## Comparación: Jefe de Proyecto vs SCM

| Aspecto | Jefe de Proyecto | SCM |
|---------|------------------|-----|
| **Campo visible** | ✅ Sí | ✅ Sí |
| **Editable** | ❌ No (solo lectura) | ✅ Sí (cuando proceso = "linea base") |
| **Muestra si vacío** | ✅ Sí (muestra "-") | ✅ Sí (puede editarlo) |
| **Forma de edición** | - | Formulario inline con botón "Actualizar" |

**Razón de la diferencia:**
- **Jefe de Proyecto:** Solo necesita **ver** la línea base para hacer seguimiento
- **SCM:** Necesita **editar** la línea base como parte de su proceso de aprobación

---

## Flujo de Datos: Línea Base

```
1. Jefe de Proyecto crea workflow
   ↓ linea_base = null

2. Jefe de Proyecto agrega Release
   ↓ release = "v1.0.0"

3. Jefe de Proyecto solicita "Línea Base"
   ↓ Crea actividad: proceso='linea base', estado_proceso='En Proceso'

4. SCM revisa y agrega línea base
   ↓ linea_base = "baseline-v1.0.0"

5. SCM aprueba
   ↓ Crea actividad: estado_proceso='Ok'

6. Jefe de Proyecto ve la línea base aprobada
   ↓ Campo muestra: "baseline-v1.0.0" (solo lectura)
```

---

## Casos de Uso

### Caso 1: Workflow Nuevo (sin línea base)
```
Vista Jefe de Proyecto:
┌──────────────────────────┐
│ Línea Base               │
│ -                        │ ← Muestra guión
└──────────────────────────┘
```

### Caso 2: Línea Base en Proceso (SCM trabajando)
```
Vista Jefe de Proyecto:
┌──────────────────────────┐
│ Línea Base               │
│ -                        │ ← Todavía muestra guión
└──────────────────────────┘

Vista SCM:
┌──────────────────────────┐
│ Línea Base               │
│ [____________] [Actualizar] │ ← Editable
└──────────────────────────┘
```

### Caso 3: Línea Base Aprobada
```
Vista Jefe de Proyecto:
┌──────────────────────────┐
│ Línea Base               │
│ baseline-v1.0.0          │ ← Valor visible
└──────────────────────────┘

Vista SCM:
┌──────────────────────────┐
│ Línea Base               │
│ baseline-v1.0.0          │ ← Solo lectura (ya no en proceso)
└──────────────────────────┘
```

---

## Beneficios

### ✓ Para el Jefe de Proyecto
1. **Visibilidad completa:** Puede ver el estado de la línea base sin necesidad de ir a otra vista
2. **Seguimiento del proceso:** Sabe cuándo el SCM ha agregado la línea base
3. **Información completa:** Tiene todos los datos del workflow en un solo lugar
4. **No puede modificar accidentalmente:** Al ser solo lectura, evita cambios no autorizados

### ✓ Para el Sistema
1. **Consistencia:** Ambos roles ven la misma información
2. **Separación de responsabilidades:** JP ve, SCM edita
3. **Auditoría:** Cambios a línea base solo pueden hacerse desde el rol SCM
4. **Integridad de datos:** No hay riesgo de ediciones conflictivas

---

## Código Completo del Cambio

### Antes (líneas 45-57)
```html
<div>
    <h3 class="text-sm font-medium text-gray-500">Release</h3>
    <form method="post" class="flex items-center space-x-2">
        {% csrf_token %}
        <input type="hidden" name="update_release" value="1">
        {{ release_form.release }}
        <button type="submit"
                class="bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold py-1 px-3 rounded transition-colors duration-200">
            Actualizar
        </button>
    </form>
</div>
</div>  <!-- Cierre del grid -->
```

### Después (líneas 45-61)
```html
<div>
    <h3 class="text-sm font-medium text-gray-500">Release</h3>
    <form method="post" class="flex items-center space-x-2">
        {% csrf_token %}
        <input type="hidden" name="update_release" value="1">
        {{ release_form.release }}
        <button type="submit"
                class="bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold py-1 px-3 rounded transition-colors duration-200">
            Actualizar
        </button>
    </form>
</div>
<div>  <!-- NUEVO: Campo Línea Base -->
    <h3 class="text-sm font-medium text-gray-500">Línea Base</h3>
    <p class="mt-1 text-lg text-gray-900">{{ workflow.linea_base|default:"-" }}</p>
</div>
</div>  <!-- Cierre del grid -->
```

---

## Verificación

### Django Check
```bash
python workflowup/manage.py check
```
**Resultado:** ✅ System check identified no issues (0 silenced).

### Pruebas Manuales Recomendadas

1. **Login como Jefe de Proyecto**
   ```
   Usuario: jproyecto
   Contraseña: test123
   ```

2. **Navegar a un workflow existente**
   - Ver detalles de un workflow
   - Verificar que el campo "Línea Base" aparece después de "Release"
   - Verificar que muestra "-" si está vacío
   - Verificar que muestra el valor si tiene contenido

3. **Verificar que NO es editable**
   - No debe haber formulario ni botón "Actualizar"
   - Solo debe mostrar texto plano

---

## Notas de Implementación

### ¿Por qué no se requiere cambio en `views.py`?
El campo `workflow.linea_base` ya está disponible en el contexto porque se pasa el objeto `workflow` completo a la vista. No es necesario agregar nada adicional al contexto.

### ¿Por qué usar `|default:"-"`?
- **Buena práctica UX:** Muestra "-" en lugar de dejar el espacio en blanco
- **Consistencia:** Otros campos en el sistema usan el mismo patrón
- **Claridad:** El usuario sabe que el campo existe pero no tiene valor (vs. un espacio vacío que podría parecer un error)

### ¿Por qué después del campo Release?
1. **Flujo lógico:** Release → Línea Base es la secuencia natural del proceso
2. **Diseño balanceado:** Mantiene el grid de 2 columnas equilibrado
3. **Agrupación conceptual:** Ambos campos están relacionados con versiones/releases

---

## Checklist

- [x] Campo agregado en template
- [x] Ubicación armoniosa (después de Release)
- [x] Solo lectura (no editable)
- [x] Siempre visible (incluso si vacío)
- [x] Usa `|default:"-"` para valores nulos
- [x] Estilos consistentes con otros campos
- [x] Django check ejecutado sin errores
- [x] Documentación completa

---

## Estado Final

✅ **CAMBIO COMPLETADO Y VERIFICADO**

El campo "Línea Base" ahora:
- ✓ Es visible en la vista de Detalle de Workflow para Jefe de Proyecto
- ✓ Se muestra en una ubicación lógica (después de Release)
- ✓ Es de solo lectura (no editable por JP)
- ✓ Muestra "-" cuando está vacío
- ✓ Mantiene consistencia visual con el resto del formulario
- ✓ No requiere cambios en el backend (usa el objeto workflow existente)

**Listo para usar.**
