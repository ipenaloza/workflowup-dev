<objective>
Implementar funcionalidad completa de reportería para el rol "Administrador" en el dashboard de WorkflowUp. Esta vista debe proporcionar análisis estadístico comprensivo de workflows y actividades, con capacidades de filtrado dinámico y exportación a CSV.

El dashboard servirá como herramienta de monitoreo y análisis para administradores del sistema, permitiendo visualizar el estado general de todos los workflows, analizar patrones de proceso/estado, y exportar datos para análisis externo.
</objective>

<context>
Proyecto: WorkflowUp - Django 5.2.8 con MySQL 8.0
URL objetivo: `/workflow` (vista para rol "Administrador")
Template: `workflowup/workflow/templates/workflow/dashboard.html`
Vista: `workflowup/workflow/views.py` - función `dashboard`

Antes de comenzar, lee el archivo CLAUDE.md para entender las convenciones del proyecto, la estructura de modelos, y las mejores prácticas establecidas.

Modelos relevantes:
- `Workflow` (tabla: workflows) - Información principal de workflows
- `Actividad` (tabla: actividades) - Registro de actividades y estados

Campos clave de Actividad:
- `workflow` (FK) - Relación con Workflow
- `estado_workflow` - Valores: "Nuevo", "Activo", "Cerrado", "Cancelado"
- `proceso` - Valores según PROCESO_CHOICES: "linea base", "RM Rev", "Diff Info", "QA"
- `estado_proceso` - Valores: "En Proceso", "Ok", "No Ok"
- `fecha` (DateTime) - Timestamp de la actividad
- `usuario` - Username del usuario que creó la actividad

Campos clave de Workflow:
- `id_workflow` (PK)
- `id_proyecto` - ID del proyecto
- `nom_proyecto` - Nombre del proyecto
- `componente` - Componente del proyecto
- `created_at` - Fecha de creación
</context>

<requirements>

## 1. Estructura de la Vista (3 Secciones)

### Sección 1: Tarjetas de Resumen (Superior)
Mostrar 5 tarjetas en una sola línea horizontal con estadísticas de workflows únicos de la tabla Actividad:

1. **Total Workflow**: Conteo de workflows únicos (COUNT DISTINCT workflow_id)
2. **Total Workflow Nuevos**: Workflows con estado_workflow = "Nuevo"
3. **Total Workflow Activos**: Workflows con estado_workflow = "Activo"
4. **Total Workflow Cerrados**: Workflows con estado_workflow = "Cerrado"
5. **Total Workflow Cancelados**: Workflows con estado_workflow = "Cancelado"

**Importante**: Para cada workflow único, usar solo la actividad más reciente (fecha más alta) para determinar su estado actual.

### Sección 2: Matriz de Proceso/Estado
Debajo de las tarjetas, mostrar una matriz visual con todas las combinaciones posibles de:
- Filas: Procesos (linea base, RM Rev, Diff Info, QA)
- Columnas: Estados de proceso (En Proceso, Ok, No Ok)
- Celdas: Conteo de workflows en cada combinación

**Importante**:
- Usar solo la última actividad de cada workflow único
- Mostrar TODAS las combinaciones (incluir ceros para combinaciones sin datos)
- Diseño tipo grid/matriz, agradable a la vista

### Sección 3: Lista Detallada con Filtros
Tabla completa mostrando datos cruzados de Workflow + Actividad:
- Campos a mostrar: id_workflow, nom_proyecto, componente, id_proyecto, estado_workflow, proceso, estado_proceso, usuario, fecha, comentario

**Panel de Filtros** (encima de la tabla):
- Rango de fechas: Desde/Hasta (basado en workflow.created_at)
- Estado Workflow: Dropdown (Nuevo/Activo/Cerrado/Cancelado/Todos)
- Usuario: Dropdown o input de texto
- ID Proyecto: Input de texto
- Nombre Proyecto: Input de texto
- Componente: Input de texto
- Botón "Aplicar Filtros" + Botón "Limpiar Filtros"

## 2. Funcionalidad de Filtrado Dinámico

**Requisito crítico**: Los filtros deben actualizar las 3 secciones sin recargar la página:
- Sección 1 (tarjetas) debe recalcular estadísticas con datos filtrados
- Sección 2 (matriz) debe recalcular conteos con datos filtrados
- Sección 3 (tabla) debe mostrar solo registros filtrados

**Implementación**:
- Usar AJAX con JavaScript vanilla o Alpine.js (según convenciones del proyecto)
- Crear endpoint API en views.py que retorne JSON con:
  - Estadísticas para tarjetas
  - Datos para matriz
  - Lista de workflows/actividades filtrados
- El frontend debe actualizar las 3 secciones dinámicamente al recibir respuesta

## 3. Exportación a CSV

Botón "Exportar CSV" que descargue el contenido actual de la Sección 3 (lista detallada):
- Incluir SOLO los registros visibles después de aplicar filtros
- Headers: ID Workflow, Proyecto, Componente, ID Proyecto, Estado Workflow, Proceso, Estado Proceso, Usuario, Fecha, Comentario
- Formato: CSV estándar con codificación UTF-8
- Nombre de archivo: `workflows_report_YYYYMMDD_HHMMSS.csv`

</requirements>

<implementation>

## Estructura de Archivos a Modificar/Crear

1. **Backend (workflowup/workflow/views.py)**:
   - Modificar la vista `dashboard` existente para rol "Administrador"
   - Crear nueva vista API `dashboard_api` para AJAX (retorna JSON)
   - Crear vista `export_csv` para descarga de CSV

2. **Frontend (workflowup/workflow/templates/workflow/dashboard.html)**:
   - Reestructurar template existente con las 3 secciones
   - Agregar JavaScript para manejo de filtros y AJAX
   - Implementar actualización dinámica de estadísticas y tabla

3. **URLs (workflowup/workflow/urls.py)**:
   - Agregar rutas para API y CSV export

## Consideraciones Técnicas

### Queries Eficientes
- Para obtener la última actividad por workflow: usar `annotate()` con `Max('fecha')` y luego filtrar
- Evitar N+1 queries: usar `select_related()` y `prefetch_related()`
- Considerar crear un queryset base reutilizable con los filtros aplicados

### Manejo de Estado de Workflow
**CRÍTICO**: El estado actual de un workflow se determina por su actividad más reciente (fecha máxima). No asumir que la última actividad insertada es la más reciente por fecha.

```python
# Ejemplo de query correcta:
from django.db.models import Max, OuterRef, Subquery

latest_activity = Actividad.objects.filter(
    workflow=OuterRef('pk')
).order_by('-fecha')

workflows_with_latest = Workflow.objects.annotate(
    latest_activity_id=Subquery(latest_activity.values('id')[:1])
)
```

### Filtrado
- Aplicar filtros de manera condicional (solo si el parámetro está presente)
- Para rangos de fecha: usar `__gte` y `__lte`
- Para texto: usar `__icontains` para búsqueda case-insensitive
- Manejar casos donde no hay datos (mostrar mensaje apropiado)

### CSV Export
- Usar el módulo `csv` de Python
- Configurar `HttpResponse` con `content_type='text/csv'`
- Añadir header `Content-Disposition` para descarga
- Escapar correctamente caracteres especiales en CSV

### Frontend
- Manejar estados de carga durante peticiones AJAX (mostrar spinner o deshabilitar botones)
- Validar fechas en el frontend antes de enviar
- Mostrar mensajes de error si la petición AJAX falla
- Actualizar URL con parámetros de filtro (opcional, para compartibilidad)

## Patrones a Seguir

1. **Decoradores**: La vista debe mantener `@login_required` y verificar role == "Administrador"
2. **CSRF**: Incluir token CSRF en peticiones AJAX POST
3. **Mensajes**: No es necesario usar Django messages para operaciones AJAX
4. **Errores**: Retornar JSON con estructura `{"success": bool, "error": str, "data": dict}`
5. **Permisos**: Verificar permisos en TODAS las vistas (dashboard, API, CSV export)

## Lo que NO hacer (y por qué)

- **NO modificar modelos**: Los modelos Workflow y Actividad ya existen y están en uso
- **NO eliminar funcionalidad existente**: El dashboard puede tener contenido para otros roles, preservarlo
- **NO usar Django REST Framework**: El proyecto no lo usa, mantener consistencia con vistas basadas en funciones
- **NO crear archivos CSV en disco**: Generar en memoria y stream directamente en la respuesta HTTP para evitar problemas de limpieza y concurrencia
- **NO hacer queries individuales en loops**: Causaría N+1 problem y mal rendimiento

</implementation>

<output>
Modificar/crear los siguientes archivos:

1. `./workflowup/workflow/views.py`
   - Actualizar función `dashboard()` con lógica para administrador
   - Crear función `dashboard_api()` para endpoint AJAX
   - Crear función `export_workflows_csv()` para descarga CSV

2. `./workflowup/workflow/templates/workflow/dashboard.html`
   - Reestructurar con 3 secciones (tarjetas, matriz, tabla)
   - Agregar panel de filtros
   - Incluir JavaScript para AJAX y actualización dinámica
   - Agregar botón de exportación CSV

3. `./workflowup/workflow/urls.py`
   - Añadir ruta `dashboard-api/` apuntando a `dashboard_api` view
   - Añadir ruta `export-csv/` apuntando a `export_workflows_csv` view

</output>

<styling_guidelines>
Usar Tailwind CSS (CDN) según las convenciones del proyecto:

- **Tarjetas**: Diseño tipo card con bordes, sombras sutiles, padding generoso
- **Matriz**: Grid layout con celdas bien definidas, headers destacados
- **Tabla**: Diseño responsivo, zebra striping alternando colores de filas
- **Filtros**: Formulario organizado en grid, inputs con estilos consistentes
- **Botones**: Colores según acción (primario para aplicar, secundario para limpiar, verde para exportar)
- **Responsive**: Tarjetas deben stack en móviles, tabla con scroll horizontal si necesario

Priorizar funcionalidad sobre estética (MVP funcional), pero mantener consistencia visual con el resto de la aplicación.
</styling_guidelines>

<validation>
Antes de declarar el trabajo completo, verificar:

1. **Backend**:
   - [ ] Queries retornan solo la última actividad por workflow
   - [ ] Filtros se aplican correctamente (probar cada combinación)
   - [ ] Endpoint API retorna JSON válido con estructura correcta
   - [ ] CSV se genera con datos filtrados actuales
   - [ ] Permisos verificados en todas las vistas (solo Administrador)

2. **Frontend**:
   - [ ] Las 3 secciones se actualizan dinámicamente al filtrar
   - [ ] Filtros se pueden limpiar y restaurar vista completa
   - [ ] Botón CSV descarga archivo con datos correctos
   - [ ] No hay errores en consola del navegador
   - [ ] Manejo de estados de carga es visible

3. **Integración**:
   - [ ] La vista funciona solo para usuarios con role="Administrador"
   - [ ] Otros roles siguen viendo su dashboard correspondiente
   - [ ] URLs se resuelven correctamente
   - [ ] No hay conflictos con vistas existentes

4. **Testing Manual**:
   - [ ] Probar con datos de prueba (usar setup_users.py y crear workflows de prueba)
   - [ ] Verificar cálculos de estadísticas manualmente
   - [ ] Probar todos los filtros individualmente y en combinación
   - [ ] Verificar CSV con diferentes conjuntos de filtros
   - [ ] Probar en diferentes navegadores (Chrome, Firefox)

</validation>

<success_criteria>
El trabajo está completo cuando:

1. El dashboard para Administrador muestra las 3 secciones con datos correctos
2. Los filtros actualizan dinámicamente las estadísticas, matriz y tabla sin recargar la página
3. El botón de exportación CSV descarga un archivo con los datos filtrados actuales
4. Todas las queries son eficientes (sin N+1 problems)
5. El código sigue las convenciones del proyecto Django establecidas en CLAUDE.md
6. La funcionalidad es accesible solo para usuarios con role="Administrador"
7. Otros roles no se ven afectados y siguen viendo su dashboard correspondiente

**Definición de "correcto" para conteos**: Los conteos deben basarse en la última actividad por fecha (no por ID) para cada workflow único, aplicando los filtros seleccionados por el usuario.
</success_criteria>

<workflow_tips>
Orden sugerido de implementación:

1. **Fase 1 - Backend Base**:
   - Crear queries para obtener última actividad por workflow
   - Implementar lógica de cálculo de estadísticas
   - Crear estructura de datos para matriz

2. **Fase 2 - Vista Inicial (sin filtros)**:
   - Modificar vista dashboard para pasar datos al template
   - Reestructurar template con las 3 secciones
   - Implementar renderizado estático de tarjetas, matriz y tabla

3. **Fase 3 - Filtrado Dinámico**:
   - Crear endpoint API con lógica de filtros
   - Implementar JavaScript para capturar filtros y hacer petición AJAX
   - Conectar respuesta API con actualización de DOM

4. **Fase 4 - Exportación CSV**:
   - Crear vista de exportación aplicando los mismos filtros
   - Agregar botón y enlace en template
   - Probar descarga con diferentes conjuntos de filtros

5. **Fase 5 - Refinamiento**:
   - Agregar estados de carga
   - Mejorar estilos visuales
   - Testing exhaustivo
   - Documentar cualquier consideración especial

Procede implementando todas las fases en secuencia. Si encuentras inconsistencias o indefiniciones, pregunta antes de continuar.
</workflow_tips>
