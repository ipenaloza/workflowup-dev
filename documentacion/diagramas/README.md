# Diagramas UML - Dashboard de Reportería (Administrador)

## Descripción

Este directorio contiene los diagramas UML completos en formato PlantUML para la funcionalidad de reportería del dashboard de Administrador implementada en WorkflowUp.

Los diagramas fueron generados siguiendo estándares UML 2.5 y reflejan fielmente la implementación real del sistema.

## Archivos Disponibles

### 1. `casos-uso-reporteria.puml` (117 líneas)
**Diagrama de Casos de Uso**

Describe los casos de uso principales del dashboard de reportería desde la perspectiva del Administrador.

**Incluye:**
- 3 actores: Administrador, Sistema Django, Base de Datos MySQL
- 11 casos de uso (7 principales + 4 de sistema)
- Relaciones: `<<include>>` y `<<extend>>`
- Notas explicativas de funcionalidades clave

**Casos de uso principales:**
1. Ver Dashboard de Reportería
2. Visualizar Estadísticas Generales (5 tarjetas)
3. Visualizar Matriz Proceso/Estado (4x3)
4. Consultar Lista de Actividades Históricas
5. Aplicar Filtros (7 criterios)
6. Limpiar Filtros
7. Exportar Datos a CSV

---

### 2. `secuencia-reporteria.puml` (562 líneas)
**Diagramas de Secuencia**

Contiene 4 diagramas de secuencia completos que describen los flujos principales del sistema.

**Secuencia 1: Carga Inicial del Dashboard**
- Flujo desde que el Administrador accede a `/workflow`
- Autenticación y verificación de permisos
- Carga de workflows con última actividad
- Cálculo de estadísticas, matriz y detalles
- Renderizado del template HTML

**Secuencia 2: Aplicar Filtros (AJAX)**
- Captura de datos del formulario
- Request AJAX a `/workflow/dashboard-api/`
- Aplicación de filtros múltiples
- Actualización dinámica del DOM sin recargar
- Actualización de tarjetas, matriz y tabla

**Secuencia 3: Exportar a CSV**
- Construcción de URL con parámetros de filtros
- Consulta de TODAS las actividades históricas
- Generación de archivo CSV con timestamp
- Descarga del archivo en el navegador

**Secuencia 4: Limpiar Filtros**
- Limpieza del formulario
- Re-aplicación sin filtros
- Recarga de datos completos
- Actualización del dashboard

**Participantes:**
- Administrador (actor)
- Navegador Web
- JavaScript (dashboard.js)
- Django Views / API Endpoint
- Helper Functions
- ORM Django
- Base de Datos MySQL
- Módulo CSV Python

---

### 3. `clases-reporteria.puml` (341 líneas)
**Diagrama de Clases**

Arquitectura completa del sistema organizada en capas Entity-Control-Boundary (MVC).

**Capa Entity (Modelos):**
- `Workflow` - Modelo principal de workflows
- `Actividad` - Log inmutable de actividades
- `PlanPruebaQA` - Plan de pruebas QA
- Relaciones: 1 Workflow → N Actividades
- Relaciones: 1 Workflow → N PlanPruebaQA

**Capa Control (Vistas y Lógica):**
- `DashboardView` - Vista principal con 3 funciones
  - `dashboard()` - Renderizado inicial
  - `dashboard_api()` - Endpoint AJAX
  - `export_workflows_csv()` - Exportación CSV
- `HelperFunctions` - 5 funciones auxiliares
  - `_get_workflows_with_latest_activity()`
  - `_apply_admin_filters()`
  - `_calculate_workflow_stats()`
  - `_calculate_process_state_matrix()`
  - `_prepare_workflow_details()`

**Capa Boundary (Interfaz):**
- `DashboardTemplate` - Template HTML/JavaScript
  - Elementos DOM (tarjetas, matriz, tabla, formulario)
  - Métodos JavaScript (renderizar, filtrar, exportar)

**Objetos de Transferencia de Datos (DTOs):**
- `StatsData` - Datos de estadísticas (5 valores)
- `MatrixData` - Matriz proceso/estado (4x3)
- `MatrixRow` - Fila de matriz (3 valores)
- `WorkflowDetail` - Detalle de actividad
- `WorkflowWithLatestActivity` - Workflow con última actividad

**Patrones de diseño:**
- MVC (Model-View-Controller)
- Helper Functions (reutilización)
- DTO (transferencia de datos)
- AJAX (comunicación asíncrona)

---

## Cómo Visualizar los Diagramas

### Opción 1: PlantUML Web Server (Más rápido)

1. Visita: http://www.plantuml.com/plantuml/uml/
2. Copia y pega el contenido del archivo `.puml`
3. Click en "Submit" para generar el diagrama
4. Descarga como PNG, SVG o PDF

### Opción 2: Visual Studio Code

1. Instala la extensión "PlantUML" de jebbs
2. Abre el archivo `.puml` en VSCode
3. Presiona `Alt+D` (Windows/Linux) o `Option+D` (Mac)
4. El preview se mostrará en el panel lateral
5. Click derecho → "Export Current Diagram" para guardar

### Opción 3: IntelliJ IDEA / PyCharm

1. Instala el plugin "PlantUML integration"
2. Abre el archivo `.puml`
3. El preview se mostrará automáticamente
4. Click derecho → "Export to..." para guardar

### Opción 4: Línea de Comandos

```bash
# Instalar PlantUML (requiere Java)
brew install plantuml  # macOS
apt-get install plantuml  # Ubuntu/Debian

# Generar PNG
plantuml casos-uso-reporteria.puml
plantuml secuencia-reporteria.puml
plantuml clases-reporteria.puml

# Generar SVG (vectorial)
plantuml -tsvg casos-uso-reporteria.puml
plantuml -tsvg secuencia-reporteria.puml
plantuml -tsvg clases-reporteria.puml
```

---

## Estadísticas de los Diagramas

| Diagrama | Líneas | Elementos Principales |
|----------|--------|----------------------|
| Casos de Uso | 117 | 3 actores, 11 casos de uso |
| Secuencias | 562 | 4 secuencias completas |
| Clases | 341 | 13 clases, 4 packages |
| **TOTAL** | **1,020** | **28 elementos principales** |

---

## Relación con el Código Fuente

Los diagramas reflejan la implementación real ubicada en:

- **Views**: `/workflowup/workflow/views.py` (líneas 18-260, 1019-1305)
  - `dashboard()` - líneas 18-260
  - `dashboard_api()` - líneas 1199-1238
  - `export_workflows_csv()` - líneas 1245-1305
  - Helper functions - líneas 1023-1192

- **Template**: `/workflowup/workflow/templates/workflow/dashboard.html`
  - HTML structure - líneas 1-239
  - JavaScript AJAX - líneas 242-391

- **Models**: `/workflowup/workflow/models.py`
  - `Workflow` - líneas 9-79
  - `Actividad` - líneas 124-192
  - `PlanPruebaQA` - líneas 81-122

- **URLs**: `/workflowup/workflow/urls.py`
  - `dashboard` → `/workflow/`
  - `dashboard_api` → `/workflow/dashboard-api/`
  - `export_workflows_csv` → `/workflow/export-csv/`

---

## Características Técnicas Representadas

### Autenticación y Autorización
- `@login_required` decorator en todas las vistas
- Verificación `role == "Administrador"`
- Redirección según rol del usuario

### Filtros Múltiples (7 criterios)
1. Fecha desde / Fecha hasta
2. Estado workflow (Nuevo, Activo, Cerrado, Cancelado)
3. Usuario (dropdown con todos los usuarios del sistema)
4. ID Proyecto (búsqueda por substring, case-insensitive)
5. Nombre Proyecto (búsqueda por substring, case-insensitive)
6. Componente (búsqueda por substring, case-insensitive)

### Estadísticas (5 tarjetas)
1. Total Workflows
2. Nuevos
3. Activos
4. Cerrados
5. Cancelados

### Matriz Proceso/Estado (4x3)
**Procesos:**
1. Línea Base
2. RM Rev
3. Diff Info
4. QA

**Estados:**
1. En Proceso
2. Ok
3. No Ok

### Tabla de Actividades
- Muestra TODAS las actividades históricas (no solo la última)
- 10 columnas de datos
- Ordenamiento: fecha DESC, workflow_id, id_actividad DESC
- Badges con colores según estado

### Funcionalidad AJAX
- Actualización sin recargar página
- Loading indicator durante requests
- Manejo de errores con alertas
- Actualización de stats, matriz y tabla simultánea

### Exportación CSV
- Mantiene filtros aplicados
- TODAS las actividades históricas (completo)
- UTF-8 BOM para Excel compatibility
- Timestamp en nombre del archivo
- 10 columnas: ID, Proyecto, Componente, etc.

---

## Notas de Implementación

### Datos Completos vs. Última Actividad
Los diagramas reflejan una característica crítica del sistema:

- **Para filtrado y estadísticas**: Se usa la ÚLTIMA actividad de cada workflow
- **Para exportación y tabla**: Se muestran TODAS las actividades históricas

Esta distinción es importante porque:
1. Las tarjetas y matriz muestran el estado ACTUAL de cada workflow
2. La tabla muestra el HISTORIAL COMPLETO de cambios
3. El CSV exporta el HISTORIAL COMPLETO para auditoría

### Query Optimization
Los diagramas muestran el uso de:
- `prefetch_related('actividades')` - Reduce N+1 queries
- `select_related('workflow')` - Join para actividades
- Subqueries para última actividad
- Order by fecha DESC para obtener últimas actividades

### Seguridad
- CSRF token en requests AJAX
- Verificación de autenticación en cada endpoint
- Verificación de rol de Administrador
- PermissionDenied para accesos no autorizados

---

## Validación de Diagramas

### Compilación
Todos los diagramas han sido validados con sintaxis PlantUML correcta y son compilables.

### Estándares UML 2.5
- Casos de uso: Notación estándar con actores, casos de uso, y relaciones
- Secuencias: Participantes, activaciones, mensajes, retornos
- Clases: Atributos, métodos, relaciones, packages, estereotipos

### Reflexión del Código
Los diagramas reflejan fielmente:
- Estructura de clases y métodos reales
- Flujo de datos exacto
- Parámetros y retornos de funciones
- Interacciones entre componentes

---

## Contacto

Para preguntas o aclaraciones sobre estos diagramas, referirse a:
- `CLAUDE.md` - Guía completa del proyecto
- `README.md` - Documentación general
- `IMPLEMENTATION_SUMMARY.md` - Detalles técnicos

---

**Generado**: 2025-12-16
**Versión**: 1.0
**Sistema**: WorkflowUp 2.0 (Django 5.2.8)
**Herramienta**: PlantUML
**Estándar**: UML 2.5
