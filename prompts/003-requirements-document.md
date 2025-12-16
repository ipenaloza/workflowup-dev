<objective>
Generar un documento de requerimientos completo y profesional en formato estándar IEEE/ISO para la funcionalidad de reportería del dashboard de Administrador implementada en WorkflowUp.

El documento debe seguir las mejores prácticas de ingeniería de software, incluyendo requerimientos funcionales, no funcionales, casos de uso, restricciones técnicas, y criterios de aceptación.
</objective>

<context>
Funcionalidad implementada: Dashboard de reportería para rol Administrador
Ubicación: `/workflow` (URL)
Componentes:
- 5 tarjetas de resumen de workflows
- Matriz de proceso/estado
- Lista detallada de actividades históricas
- Sistema de filtros dinámicos (AJAX)
- Exportación CSV

Tecnologías:
- Django 5.2.8
- MySQL 8.0
- Tailwind CSS
- JavaScript Vanilla
- AJAX

Modelos de datos:
- Workflow (tabla workflows)
- Actividad (tabla actividades)
</context>

<requirements>

## Estructura del Documento de Requerimientos

El documento debe seguir esta estructura estándar:

### 1. Introducción
- 1.1 Propósito del documento
- 1.2 Alcance del sistema
- 1.3 Definiciones, acrónimos y abreviaturas
- 1.4 Referencias
- 1.5 Visión general del documento

### 2. Descripción General
- 2.1 Perspectiva del producto
- 2.2 Funciones del producto
- 2.3 Características de los usuarios
- 2.4 Restricciones
- 2.5 Suposiciones y dependencias

### 3. Requerimientos Específicos

#### 3.1 Requerimientos Funcionales
Organizar por funcionalidad:

**RF-001: Visualización de Estadísticas Generales**
- ID: RF-001
- Prioridad: Alta
- Descripción: El sistema debe mostrar tarjetas de resumen con conteos de workflows
- Entradas: Base de datos (tabla actividades)
- Procesamiento: Cálculo de workflows únicos por estado basado en última actividad
- Salidas: 5 tarjetas con conteos
- Criterios de aceptación:
  - [ ] Muestra 5 tarjetas (Total, Nuevos, Activos, Cerrados, Cancelados)
  - [ ] Usa solo la última actividad por workflow para conteo
  - [ ] Se actualiza dinámicamente con filtros

**RF-002: Matriz de Proceso/Estado**
- ID: RF-002
- Prioridad: Alta
- Descripción: ...

**RF-003: Lista Detallada de Actividades Históricas**
- ID: RF-003
- Prioridad: Alta
- Descripción: ...

**RF-004: Sistema de Filtrado Dinámico**
- ID: RF-004
- Prioridad: Alta
- Descripción: ...
- Sub-requerimientos:
  - RF-004.1: Filtro por rango de fechas
  - RF-004.2: Filtro por estado workflow
  - RF-004.3: Filtro por usuario
  - RF-004.4: Filtro por ID proyecto
  - RF-004.5: Filtro por nombre proyecto
  - RF-004.6: Filtro por componente
  - RF-004.7: Botón aplicar filtros
  - RF-004.8: Botón limpiar filtros

**RF-005: Exportación a CSV**
- ID: RF-005
- Prioridad: Media
- Descripción: ...

**RF-006: Control de Acceso**
- ID: RF-006
- Prioridad: Crítica
- Descripción: Solo usuarios con rol "Administrador" pueden acceder

#### 3.2 Requerimientos No Funcionales

**RNF-001: Rendimiento**
- El dashboard debe cargar en menos de 2 segundos con hasta 1000 workflows
- Las consultas AJAX deben responder en menos de 1 segundo
- No debe haber consultas N+1

**RNF-002: Usabilidad**
- La interfaz debe ser intuitiva sin necesidad de capacitación
- Los filtros deben tener labels descriptivos
- Estados deben usar código de colores consistente

**RNF-003: Seguridad**
- Autenticación requerida
- Verificación de rol en todas las vistas
- Protección CSRF en peticiones AJAX
- Validación de entrada en backend

**RNF-004: Mantenibilidad**
- Código modular con funciones helper reutilizables
- Documentación inline (docstrings)
- Separación de lógica de negocio y presentación

**RNF-005: Compatibilidad**
- Navegadores: Chrome 90+, Firefox 88+, Safari 14+
- Responsive: Desktop, tablet, mobile
- Codificación UTF-8 para CSV

**RNF-006: Escalabilidad**
- Debe soportar hasta 10,000 workflows
- Queries eficientes con índices
- Paginación futura si es necesario

### 4. Interfaces Externas

#### 4.1 Interfaces de Usuario
- Descripción detallada de las 3 secciones
- Mockups o referencias a pantallas

#### 4.2 Interfaces de Hardware
- N/A

#### 4.3 Interfaces de Software
- Django 5.2.8
- MySQL 8.0
- Navegadores web modernos

#### 4.4 Interfaces de Comunicación
- HTTP/HTTPS para peticiones web
- AJAX para actualizaciones dinámicas

### 5. Atributos del Sistema

#### 5.1 Confiabilidad
- Disponibilidad: 99.9%
- Tolerancia a fallos: Manejo de errores en AJAX

#### 5.2 Disponibilidad
- 24/7 (dependiente del servidor)

#### 5.3 Seguridad
- Autenticación basada en sesión Django
- Autorización por roles

#### 5.4 Mantenibilidad
- Código estructurado y documentado
- Arquitectura MVC de Django

### 6. Otros Requerimientos

#### 6.1 Requerimientos de Base de Datos
- Tablas: workflows, actividades
- Índices requeridos en workflow_id, fecha

#### 6.2 Requerimientos de Internacionalización
- Textos en español
- Formato de fecha: YYYY-MM-DD HH:MM:SS

#### 6.3 Requerimientos Legales
- N/A (sistema interno)

### 7. Apéndices

#### Apéndice A: Glosario
- **Workflow**: Flujo de trabajo de un proyecto
- **Actividad**: Registro de evento en el workflow
- **Estado Workflow**: Nuevo, Activo, Cerrado, Cancelado
- **Proceso**: Línea base, RM Rev, Diff Info, QA
- **Estado Proceso**: En Proceso, Ok, No Ok

#### Apéndice B: Modelos de Análisis
- Referencia a diagramas de casos de uso
- Referencia a diagramas de secuencia
- Referencia a diagrama de clases

#### Apéndice C: Lista de Asuntos Pendientes
- N/A o futuras mejoras (paginación, gráficos, etc.)

</requirements>

<output>
Crear el archivo:
`./documentacion/requerimientos/REQ-001-Dashboard-Reporteria-Administrador.md`

El documento debe:
- Seguir formato Markdown profesional
- Usar tablas para organizar requerimientos
- Incluir numeración jerárquica clara
- Tener TOC (Table of Contents) al inicio
- Ser completo, preciso y profesional
- Incluir metadatos del documento (versión, fecha, autores)
</output>

<formatting_guidelines>

## Formato del Documento

### Header del Documento
```markdown
# Documento de Requerimientos de Software (SRS)
## Dashboard de Reportería para Administrador - WorkflowUp

**Código del Documento:** REQ-001
**Versión:** 1.0
**Fecha:** 2025-12-16
**Estado:** Aprobado
**Autor:** Equipo de Desarrollo WorkflowUp

---

## Control de Versiones

| Versión | Fecha | Autor | Descripción de Cambios |
|---------|-------|-------|------------------------|
| 1.0 | 2025-12-16 | Equipo Dev | Versión inicial - Implementación completa |

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
   1. [Propósito del Documento](#11-propósito-del-documento)
   2. [Alcance del Sistema](#12-alcance-del-sistema)
   ...
```

### Formato de Requerimientos Funcionales
```markdown
### RF-001: Visualización de Estadísticas Generales

**Prioridad:** Alta
**Estado:** Implementado
**Categoría:** Visualización de Datos

**Descripción:**
El sistema debe mostrar cinco tarjetas de resumen que muestren estadísticas consolidadas...

**Precondiciones:**
- Usuario autenticado con rol "Administrador"
- Existen registros en la tabla actividades

**Entradas:**
- Datos de la tabla `actividades` (todos los workflows)
- Parámetros de filtro (si se aplicaron)

**Procesamiento:**
1. Obtener workflows únicos
2. Para cada workflow, obtener actividad con fecha más reciente
3. Contar workflows por estado_workflow
4. Generar estadísticas agregadas

**Salidas:**
- 5 tarjetas visuales con conteos:
  - Total Workflows
  - Workflows Nuevos
  - Workflows Activos
  - Workflows Cerrados
  - Workflows Cancelados

**Criterios de Aceptación:**
- [ ] Las 5 tarjetas se muestran en una línea horizontal
- [ ] Los conteos se basan solo en la última actividad por workflow
- [ ] Las tarjetas usan código de colores distintivo
- [ ] Se actualizan dinámicamente cuando se aplican filtros
- [ ] Los números son precisos y verificables

**Dependencias:**
- Ninguna

**Notas Técnicas:**
- Implementado en `views.py` función `_calculate_workflow_stats()`
- Template: `dashboard.html` sección superior
```

### Formato de Requerimientos No Funcionales
```markdown
### RNF-001: Rendimiento

**Categoría:** Performance
**Prioridad:** Alta

**Descripción:**
El dashboard debe proporcionar respuestas rápidas para mantener una experiencia de usuario fluida.

**Métricas:**

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Carga inicial | < 2 segundos | Tiempo hasta renderizado completo |
| Respuesta AJAX | < 1 segundo | Tiempo de respuesta API |
| Queries DB | < 100ms | Tiempo de ejecución de consultas |

**Restricciones:**
- No más de 3 consultas a base de datos por carga de página
- Uso de `select_related()` para evitar N+1
- Índices apropiados en workflow_id y fecha

**Verificación:**
- Pruebas de carga con 1000+ workflows
- Monitoreo de Django Debug Toolbar
- Análisis de queries SQL
```

</formatting_guidelines>

<success_criteria>

El documento está completo cuando:

1. ✅ Sigue estructura estándar IEEE/ISO para SRS
2. ✅ Incluye todos los requerimientos funcionales (RF-001 a RF-006 mínimo)
3. ✅ Incluye todos los requerimientos no funcionales (RNF-001 a RNF-006)
4. ✅ Cada requerimiento tiene ID único, prioridad, criterios de aceptación
5. ✅ Usa formato Markdown profesional con tablas y listas
6. ✅ Incluye TOC navegable con enlaces
7. ✅ Tiene metadatos del documento (versión, fecha, autores)
8. ✅ Es preciso y refleja la implementación real
9. ✅ Está guardado en `./documentacion/requerimientos/`
10. ✅ Es completo (8-12 páginas aproximadamente)

</success_criteria>
