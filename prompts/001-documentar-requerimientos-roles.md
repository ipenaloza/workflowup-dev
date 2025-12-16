<objective>
Analizar exhaustivamente las funcionalidades implementadas para los roles SCM (Software Configuration Manager), Release Manager (RM) y QA (Quality Assurance) en el proyecto Django WorkflowUp, y generar documentos de requerimientos estándar completos para cada rol.

Este documento servirá como especificación formal del sistema para stakeholders técnicos y no técnicos, documentando el comportamiento actual del sistema.
</objective>

<context>
Proyecto: WorkflowUp - Sistema Django 5.2.8 de gestión de workflows con RBAC (Role-Based Access Control)

Roles a documentar:
- **SCM**: Gestiona línea base (baseline) y reportes de diferencias (Diff Info)
- **Release Manager (RM)**: Realiza revisión de releases
- **QA**: Ejecuta planes de pruebas y aprueba/rechaza procesos de calidad

El proyecto está ubicado en ./workflowup/ con la siguiente estructura relevante:
- Modelo User: ./workflowup/users_admin/models.py
- Modelos Workflow: ./workflowup/workflow/models.py (Workflow, Actividad, PlanPruebaQA)
- Vistas por rol: ./workflowup/workflow/views.py
- Templates por rol: ./workflowup/workflow/templates/workflow/

Leer CLAUDE.md para comprender la arquitectura del sistema, especialmente la sección "Workflow System Architecture".
</context>

<analysis_requirements>
Para cada uno de los tres roles (SCM, RM, QA), analiza **exhaustivamente** lo siguiente:

1. **Casos de uso**: Identifica todas las operaciones que el rol puede realizar en el sistema
2. **Flujo de trabajo**: Secuencia de estados y procesos en los que participa
3. **Permisos y restricciones**: Qué puede y qué no puede hacer el rol
4. **Interacciones con otros roles**: Cómo se relaciona con Jefe de Proyecto y otros roles
5. **Reglas de negocio**: Validaciones, campos obligatorios, condiciones para aprobar/rechazar
6. **Entradas y salidas**: Datos que recibe y datos que genera
7. **Estados del sistema**: Estados de workflow y proceso que maneja

Analiza profundamente:
- Vistas específicas de cada rol en views.py
- Templates HTML específicos de cada rol
- Métodos del modelo Workflow relacionados con cada proceso
- Modelo Actividad y sus estados
- Decoradores y permisos aplicados
</analysis_requirements>

<data_sources>
Archivos críticos a examinar:
- @CLAUDE.md - Arquitectura general y reglas de negocio
- @workflowup/workflow/models.py - Modelos Workflow, Actividad, PlanPruebaQA
- @workflowup/workflow/views.py - Lógica de vistas por rol
- @workflowup/workflow/templates/workflow/dashboard_scm.html - Dashboard SCM
- @workflowup/workflow/templates/workflow/dashboard_rm.html - Dashboard RM
- @workflowup/workflow/templates/workflow/dashboard_qa.html - Dashboard QA
- @workflowup/workflow/templates/workflow/workflow_detail_scm.html - Detalle SCM
- @workflowup/workflow/templates/workflow/workflow_detail_rm.html - Detalle RM
- @workflowup/workflow/templates/workflow/workflow_detail_qa.html - Detalle QA
- @workflowup/users_admin/models.py - Modelo User y roles
</data_sources>

<output_format>
Genera TRES documentos de requerimientos (uno por rol) siguiendo el formato estándar IEEE 830 simplificado:

**Estructura de cada documento:**

```
# Documento de Requerimientos - Rol [SCM/RM/QA]
## WorkflowUp - Sistema de Gestión de Workflows

### 1. Introducción
1.1 Propósito del documento
1.2 Alcance del rol en el sistema
1.3 Definiciones, acrónimos y abreviaturas
1.4 Referencias

### 2. Descripción General del Rol
2.1 Perspectiva del rol en el sistema
2.2 Funciones principales
2.3 Características de usuarios del rol
2.4 Restricciones generales

### 3. Requerimientos Funcionales Específicos
3.1 [Funcionalidad 1]
    3.1.1 Descripción
    3.1.2 Entradas
    3.1.3 Procesamiento
    3.1.4 Salidas
    3.1.5 Reglas de negocio
    3.1.6 Validaciones

3.2 [Funcionalidad 2]
    ...

### 4. Flujo de Trabajo del Rol
4.1 Estados del workflow involucrados
4.2 Procesos asignados al rol
4.3 Transiciones de estado
4.4 Interacciones con otros roles

### 5. Interfaz de Usuario
5.1 Dashboard del rol
5.2 Vistas de detalle
5.3 Formularios y campos requeridos
5.4 Mensajes y notificaciones

### 6. Requerimientos de Datos
6.1 Modelos de datos utilizados
6.2 Campos obligatorios vs opcionales
6.3 Validaciones de datos
6.4 Relaciones entre entidades

### 7. Reglas de Negocio y Restricciones
7.1 Reglas de aprobación/rechazo
7.2 Campos obligatorios por operación
7.3 Condiciones de habilitación de botones
7.4 Restricciones de acceso

### 8. Matriz de Trazabilidad
[Tabla que relaciona funcionalidades con vistas, modelos y templates]
```

Guarda los documentos en:
- `./documentacion/requerimientos/requerimientos-rol-scm.md`
- `./documentacion/requerimientos/requerimientos-rol-rm.md`
- `./documentacion/requerimientos/requerimientos-rol-qa.md`

**Estilo de escritura:**
- Lenguaje claro, formal y profesional en español
- Enfoque en el comportamiento observable del sistema
- Incluye referencias específicas a archivos de código (ej: "views.py:376-423")
- Usa tablas para estructurar información cuando sea apropiado
- Enumera todas las validaciones y reglas de negocio explícitamente
</output_format>

<verification>
Antes de declarar la tarea completa, verifica:

1. ✓ Has leído y comprendido CLAUDE.md, especialmente la sección Workflow System Architecture
2. ✓ Has examinado todas las vistas específicas de cada rol (dashboard y detail views)
3. ✓ Has analizado los templates HTML de cada rol
4. ✓ Has revisado los modelos Workflow, Actividad y PlanPruebaQA
5. ✓ Cada documento incluye TODAS las funcionalidades del rol (no parciales)
6. ✓ Las reglas de negocio están documentadas con precisión
7. ✓ Los tres documentos están guardados en ./documentacion/requerimientos/
8. ✓ Cada documento sigue la estructura IEEE 830 especificada
9. ✓ La matriz de trazabilidad está completa
10. ✓ Referencias a código fuente incluidas donde sea relevante
</verification>

<success_criteria>
- Tres documentos de requerimientos completos generados (SCM, RM, QA)
- Cada documento cubre exhaustivamente todas las funcionalidades del rol
- Formato IEEE 830 aplicado consistentemente
- Reglas de negocio documentadas con precisión y completitud
- Referencias específicas a archivos de código incluidas
- Archivos guardados correctamente en ./documentacion/requerimientos/
- Documentos listos para ser usados por stakeholders técnicos y de negocio
</success_criteria>