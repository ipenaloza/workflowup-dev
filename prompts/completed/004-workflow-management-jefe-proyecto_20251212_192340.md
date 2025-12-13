<objective>
Implementar un sistema completo de gestión de workflows para releases de software en Django, con enfoque inicial en el rol "Jefe de Proyecto". Este sistema permitirá gestionar el flujo de aprobaciones de componentes release a través de múltiples etapas (línea base, revisión RM, informe de diferencias, y pruebas QA), con seguimiento detallado de actividades y estados.

El objetivo es crear una aplicación robusta que se integre con el sistema RBAC existente, proporcionando vistas específicas por rol y manteniendo un historial completo de todas las interacciones del workflow.
</objective>

<context>
Este es un proyecto Django 5.2.8 con sistema de usuarios personalizado y RBAC ya implementado. El proyecto tiene:
- Custom User model en `users_admin` app con 5 roles: Administrador, Jefe de Proyecto, SCM, Release Manager, QA
- Sistema de navegación basado en roles mediante context processor
- Decorador `@admin_required` para restricción de acceso
- MySQL 8.0 como base de datos
- Tailwind CSS para estilos

Lee primero el archivo CLAUDE.md para entender la arquitectura del proyecto, especialmente:
- La estructura del User model personalizado
- El sistema RBAC existente
- Las convenciones de desarrollo del proyecto
- La ubicación de manage.py en `workflowup/manage.py`
</context>

<requirements>

## 1. Modelos de Base de Datos

### Modelo: Workflow
Crear en `workflowup/workflow/models.py` el modelo principal de workflows:

**Campos:**
- `id_workflow` - PositiveIntegerField, primary_key=True
- `id_proyecto` - CharField(max_length=8)
- `nom_proyecto` - CharField(max_length=70)
- `jefe_proyecto` - CharField(max_length=15) [username del usuario]
- `desc_proyecto` - TextField()
- `componente` - CharField(max_length=30)
- `linea_base` - CharField(max_length=80, blank=True, null=True)
- `release` - CharField(max_length=80, blank=True, null=True)
- `creacion` - DateField(auto_now_add=True)
- `qa_estimado` - DateField()
- `pap_estimado` - DateField()

**Validaciones Django:**
- Validar que `pap_estimado > qa_estimado` usando clean() method
- Validar que `jefe_proyecto` corresponda a un usuario existente

**Meta:**
- ordering = ['-creacion']
- verbose_name = 'Workflow'
- verbose_name_plural = 'Workflows'

### Modelo: PlanPruebaQA
Relación: ForeignKey a Workflow (one-to-many)

**Campos:**
- `workflow` - ForeignKey(Workflow, on_delete=CASCADE, related_name='plan_pruebas')
- `id_prueba` - PositiveSmallIntegerField() [correlativo por workflow]
- `prueba` - CharField(max_length=80)
- `avance` - CharField(max_length=4, default='0%')
- `resultado` - CharField(max_length=20, choices=[('No iniciado', 'No iniciado'), ('En proceso', 'En proceso'), ('Ok', 'Ok'), ('No Ok', 'No Ok')], default='No iniciado')

**Meta:**
- ordering = ['id_prueba']
- unique_together = [['workflow', 'id_prueba']]

### Modelo: Actividad
Relación: ForeignKey a Workflow (one-to-many)

**Campos:**
- `workflow` - ForeignKey(Workflow, on_delete=CASCADE, related_name='actividades')
- `id_actividad` - PositiveIntegerField() [correlativo por workflow]
- `fecha` - DateTimeField(auto_now_add=True)
- `usuario` - CharField(max_length=15) [username]
- `estado_workflow` - CharField(max_length=20, choices=[('Nuevo', 'Nuevo'), ('Activo', 'Activo'), ('Cancelado', 'Cancelado'), ('Cerrado', 'Cerrado')], null=True, blank=True)
- `proceso` - CharField(max_length=20, choices=[('linea base', 'Línea Base'), ('RM Rev', 'Revisión RM'), ('Diff Info', 'Informe Diferencias'), ('QA', 'Pruebas QA')], null=True, blank=True)
- `estado_proceso` - CharField(max_length=20, choices=[('No Iniciado', 'No Iniciado'), ('En Proceso', 'En Proceso'), ('Ok', 'Ok'), ('No Ok', 'No Ok')], null=True, blank=True)
- `actividad` - CharField(max_length=35)
- `comentario` - CharField(max_length=200, blank=True, null=True)

**Meta:**
- ordering = ['-fecha']
- unique_together = [['workflow', 'id_actividad']]

**Métodos del modelo Workflow:**
Implementar métodos helper para obtener los "registros de actividad" mencionados en el punto 4:
- `get_actividad_workflow()` - última actividad general
- `get_actividad_scm1()` - última actividad con proceso='linea base'
- `get_actividad_rm()` - última actividad con proceso='RM Rev'
- `get_actividad_scm2()` - última actividad con proceso='Diff Info'
- `get_actividad_qa()` - última actividad con proceso='QA'

Estos métodos deben retornar la actividad más reciente por fecha para el workflow correspondiente.

## 2. Formularios

### WorkflowCreateForm
En `workflowup/workflow/forms.py`:

**Campos visibles:**
- id_proyecto, nom_proyecto, desc_proyecto, componente, qa_estimado, pap_estimado, release (opcional)

**Validación custom:**
- `clean()` method que valide `pap_estimado > qa_estimado` con mensaje de error claro

**Campos automáticos (no en form):**
- `jefe_proyecto` se asigna desde request.user.username en la view
- `creacion` se asigna automáticamente por el modelo
- `linea_base` se deja como NULL

### PlanPruebaCreateForm
Formulario simple para agregar una prueba:
- Solo campo `prueba` visible
- `id_prueba` correlativo automático en la view
- `avance` fijado a '0%'
- `resultado` fijado a 'No iniciado'

## 3. Vistas y URLs

### Modificar vista dashboard existente
En `workflowup/workflow/views.py`, modificar la vista del dashboard para detectar el rol y renderizar templates diferentes:

```python
@login_required
def dashboard(request):
    if request.user.role == 'Administrador':
        return render(request, 'workflow/dashboard.html')
    elif request.user.role == 'Jefe de Proyecto':
        # Lógica para Jefe de Proyecto
        return render(request, 'workflow/dashboard_jp.html', context)
    # Otros roles para futuro
    else:
        return render(request, 'workflow/dashboard.html')
```

### Vista: Dashboard Jefe de Proyecto
URL: `/workflow/` (misma URL, template diferente según rol)

**Lógica:**
- Filtrar workflows donde `jefe_proyecto == request.user.username`
- Excluir workflows cuyo último `estado_workflow` sea 'Cancelado' o 'Cerrado'
- Para cada workflow, obtener del "registro de actividad workflow":
  - estado_workflow
  - proceso (mostrar como "Actividad")
  - estado_proceso (mostrar como "Estado")

**Datos a mostrar en tabla:**
- IdWorkflow, idProyecto, nomProyecto, creación, qaEstimado, papEstimado
- Estado Workflow (desde actividad más reciente)
- Actividad (campo proceso desde actividad más reciente)
- Estado (campo estado_proceso desde actividad más reciente)
- Botón "Ver Detalles" → link a workflow_detail
- Botón "Plan de Pruebas" → link a plan_pruebas

**Navegación adicional:**
Agregar opción "Crear Workflow" en el menú de navegación (modificar context processor si es necesario, o agregar en el template)

### Vista: Crear Workflow
URL: `/workflow/create/`
Decorator: `@login_required` + validación de rol 'Jefe de Proyecto'

**Lógica POST:**
1. Validar formulario
2. Crear workflow con:
   - Datos del formulario
   - `jefe_proyecto = request.user.username`
   - `id_workflow` auto-increment o max(id_workflow) + 1
3. Crear actividad inicial:
   - `id_actividad = 1`
   - `fecha` = now()
   - `usuario = request.user.username`
   - `estado_workflow = 'Nuevo'`
   - `proceso = None`
   - `estado_proceso = None`
   - `actividad = 'Workflow creado satisfactoriamente'`
   - `comentario = None`
4. Redirect a dashboard con mensaje de éxito

### Vista: Detalle de Workflow
URL: `/workflow/<int:id_workflow>/`
Decorator: `@login_required` + validación que el usuario sea el jefe del proyecto

**Parte Superior (datos del workflow):**
- Mostrar TODOS los campos del modelo Workflow excepto `jefe_proyecto`
- Agregar campos calculados desde actividades:
  - "Estado Workflow" desde `get_actividad_workflow().estado_workflow`
  - "Línea Base" desde `get_actividad_scm1().estado_proceso` (si existe)
  - "Revisión RM" desde `get_actividad_rm().estado_proceso` (si existe)
  - "Diff Info" desde `get_actividad_scm2().estado_proceso` (si existe)
  - "QA" desde `get_actividad_qa().estado_proceso` (si existe)

**Campo editable:**
- `release` debe poder agregarse/modificarse mediante formulario inline o modal

**Parte Inferior (lista de actividades):**
- Todas las actividades del workflow ordenadas de más reciente a más antiguo
- Mostrar todos los campos EXCEPTO `comentario`
- Última columna: botón para ver comentario en modal/ventana flotante

**Botones de acción (debajo de "Ver Plan de Pruebas"):**

#### Botón 1: "Solicitar línea base"
**Activo cuando:**
- (`linea_base` IS NULL y todos los demás campos tienen datos) O
- (actividad workflow tiene `proceso='linea base'` Y `estado_proceso='No Ok'`)

**Al hacer clic:**
- Modal con opciones: Aceptar/Cancelar + campo opcional comentario (max 200 chars)
- Si Cancelar: cerrar modal sin cambios
- Si Aceptar: crear nueva actividad:
  - `estado_workflow = 'Activo'`
  - `proceso = 'linea base'`
  - `estado_proceso = 'En Proceso'`
  - `actividad = 'Re solicitud de linea base'` SI era rechazo, SINO `actividad = 'Solicitud de linea base'`
  - `comentario` = texto ingresado
  - Refresh de la vista

#### Botón 2: "Solicitar revisión RM"
**Activo cuando:**
- (actividad workflow tiene `proceso='linea base'` Y `estado_proceso='Ok'`) O
- (actividad workflow tiene `proceso='RM Rev'` Y `estado_proceso='No Ok'`)

**Al hacer clic:**
- Modal similar al botón 1
- Si Aceptar: crear actividad:
  - `estado_workflow = 'Activo'`
  - `proceso = 'RM Rev'`
  - `estado_proceso = 'En Proceso'`
  - `actividad = 'Re solicitud de Revision RM'` SI era rechazo, SINO `actividad = 'Revision RM solicitada'`
  - `comentario` = texto ingresado
  - Refresh de la vista

#### Botón 3: "Solicitar Informe de diferencia"
**Activo cuando:**
- (actividad workflow tiene `proceso='RM Rev'` Y `estado_proceso='Ok'`) O
- (actividad workflow tiene `proceso='Diff Info'` Y `estado_proceso='No Ok'`)

**Al hacer clic:**
- Modal similar
- Si Aceptar: crear actividad:
  - `estado_workflow = 'Activo'`
  - `proceso = 'Diff Info'`
  - `estado_proceso = 'En Proceso'`
  - `actividad = 'Re solicitud de Informe diferencias'` SI era rechazo, SINO `actividad = 'Informe diferencias solicitado'`
  - `comentario` = texto ingresado
  - Refresh de la vista

#### Botón 4: "Solicitar Pruebas de QA"
**Activo cuando:**
- (actividad workflow tiene `proceso='Diff Info'` Y `estado_proceso='Ok'`) O
- (actividad workflow tiene `proceso='QA'` Y `estado_proceso='No Ok'`)

**Al hacer clic:**
- Modal similar
- Si Aceptar: crear actividad:
  - `estado_workflow = 'Activo'`
  - `proceso = 'QA'`
  - `estado_proceso = 'En Proceso'`
  - `actividad = 'Re solicitud de pruebas QA'` SI era rechazo, SINO `actividad = 'Pruebas QA solicitadas'`
  - `comentario` = texto ingresado
  - Refresh de la vista

### Vista: Plan de Pruebas
URL: `/workflow/<int:id_workflow>/plan-pruebas/`
Decorator: `@login_required` + validación que el usuario sea el jefe del proyecto

**Mostrar:**
- Tabla con TODOS los campos de todas las pruebas del workflow (solo lectura)
- Botón "Agregar Prueba"

**Al agregar prueba:**
- Modal/formulario con solo campo `prueba`
- Al guardar:
  - `id_prueba` = max(id_prueba) + 1 para ese workflow
  - `avance = '0%'`
  - `resultado = 'No iniciado'`
  - Refresh de la vista

## 4. Templates

### dashboard_jp.html
Crear en `workflowup/templates/workflow/dashboard_jp.html`:
- Extender base template del proyecto
- Tabla responsive con Tailwind CSS
- Mostrar datos especificados en vista
- Botones de acción estilizados
- Link "Crear Workflow" en navegación

### workflow_detail.html
- Layout en dos partes (superior/inferior) claramente diferenciadas
- Parte superior: campos en formato de definición o card
- Campo `release` editable con indicador visual
- Parte inferior: tabla de actividades con scroll si es necesario
- Botones de estado con lógica de habilitación/deshabilitación visual
- Modales para confirmación con textarea para comentarios
- Modal flotante para mostrar comentarios de actividades

### plan_pruebas.html
- Tabla simple de solo lectura
- Botón "Agregar Prueba" destacado
- Modal para formulario de nueva prueba

## 5. URLs
Actualizar `workflowup/workflow/urls.py`:
```python
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.workflow_create, name='workflow_create'),
    path('<int:id_workflow>/', views.workflow_detail, name='workflow_detail'),
    path('<int:id_workflow>/plan-pruebas/', views.plan_pruebas, name='plan_pruebas'),
    # Endpoint AJAX para actualizar release si se usa AJAX
    path('<int:id_workflow>/update-release/', views.update_release, name='update_release'),
]
```

</requirements>

<implementation>

## Buenas Prácticas Django

1. **Usar ORM eficientemente:**
   - select_related() para ForeignKeys
   - prefetch_related() para relaciones inversas
   - Evitar N+1 queries en listados

2. **Validación robusta:**
   - Clean methods en modelos para validaciones de negocio
   - Form validation en forms.py
   - View-level validation para permisos

3. **Seguridad:**
   - CSRF tokens en todos los formularios
   - Validar permisos: solo jefe_proyecto puede ver/modificar sus workflows
   - Sanitizar inputs de usuario
   - Usar messages framework para feedback

4. **Código limpio:**
   - Métodos helper en modelos para lógica de negocio
   - Managers custom si hay queries complejas recurrentes
   - Template tags custom si hay lógica repetitiva en templates

5. **Testing:**
   - Crear signals.py si se necesita lógica post-save
   - Considerar usar django-activity-stream para auditoría (opcional)

## Estructura de Archivos a Crear/Modificar

```
workflowup/workflow/
├── models.py          [MODIFICAR: agregar 3 modelos nuevos]
├── forms.py           [CREAR: formularios]
├── views.py           [MODIFICAR: agregar vistas nuevas]
├── urls.py            [MODIFICAR: agregar URLs]
└── admin.py           [MODIFICAR: registrar modelos para admin]

workflowup/templates/workflow/
├── dashboard_jp.html          [CREAR]
├── workflow_detail.html       [CREAR]
├── workflow_create.html       [CREAR]
└── plan_pruebas.html         [CREAR]
```

## Migraciones

Después de crear los modelos:
```bash
python workflowup/manage.py makemigrations
python workflowup/manage.py migrate
```

## Consideraciones Importantes

- **Navegación por rol:** Asegúrate de que el context processor `navigation_context` incluya el link "Crear Workflow" solo para Jefe de Proyecto
- **Correlativos:** Los campos `id_actividad` e `id_prueba` deben ser correlativos POR workflow, no globales
- **Estados:** La máquina de estados está implícita en la lógica de habilitación de botones - documéntala claramente
- **UX:** Los modales deben ser claros sobre qué acción realizarán
- **Performance:** Con muchas actividades, considera paginación en la lista de actividades del detalle

</implementation>

<output>
El sistema debe quedar completamente funcional para el rol "Jefe de Proyecto" con:

1. **Modelos creados y migrados:**
   - `workflowup/workflow/models.py` con Workflow, PlanPruebaQA, Actividad

2. **Formularios implementados:**
   - `workflowup/workflow/forms.py` con WorkflowCreateForm, PlanPruebaCreateForm

3. **Vistas funcionando:**
   - `workflowup/workflow/views.py` con todas las vistas especificadas

4. **URLs configuradas:**
   - `workflowup/workflow/urls.py` actualizado

5. **Templates creados:**
   - `workflowup/templates/workflow/dashboard_jp.html`
   - `workflowup/templates/workflow/workflow_detail.html`
   - `workflowup/templates/workflow/workflow_create.html`
   - `workflowup/templates/workflow/plan_pruebas.html`

6. **Admin registrado:**
   - `workflowup/workflow/admin.py` con los 3 modelos nuevos

7. **Migraciones ejecutadas:**
   - Base de datos actualizada con nuevas tablas
</output>

<verification>
Antes de declarar completo, verificar:

1. **Modelos:**
   - [ ] Los 3 modelos están definidos correctamente con todos los campos
   - [ ] Las relaciones ForeignKey funcionan
   - [ ] Los métodos helper get_actividad_*() retornan correctamente
   - [ ] Las validaciones clean() funcionan

2. **Vistas:**
   - [ ] Dashboard JP muestra solo workflows del usuario actual
   - [ ] Filtrado por estado funciona (no muestra Cancelado/Cerrado)
   - [ ] Crear workflow genera la actividad inicial correctamente
   - [ ] Los 4 botones se habilitan según las condiciones correctas
   - [ ] Las validaciones de permisos funcionan (solo jefe puede ver sus workflows)

3. **Templates:**
   - [ ] Todos los templates renderizan sin errores
   - [ ] Los estilos Tailwind se aplican correctamente
   - [ ] Los modales abren y cierran correctamente
   - [ ] El campo release es editable

4. **Funcionalidad completa:**
   - [ ] Crear un workflow nuevo funciona
   - [ ] Ver listado en dashboard funciona
   - [ ] Ver detalle muestra todos los datos correctos
   - [ ] Los 4 botones crean actividades correctamente
   - [ ] Agregar pruebas al plan funciona
   - [ ] La navegación entre vistas funciona

5. **Testing manual:**
   - [ ] Login como usuario con rol "Jefe de Proyecto"
   - [ ] Crear un workflow completo
   - [ ] Ejecutar el flujo: línea base → RM → Diff Info → QA
   - [ ] Agregar pruebas al plan
   - [ ] Verificar que los estados se actualizan correctamente

6. **Base de datos:**
   - [ ] Ejecutar `python workflowup/manage.py check` sin errores
   - [ ] Ejecutar `python workflowup/manage.py makemigrations --dry-run` confirma que no hay migraciones pendientes
   - [ ] Inspeccionar tablas en MySQL para confirmar estructura correcta
</verification>

<success_criteria>
✓ Usuario con rol "Jefe de Proyecto" puede:
  - Ver dashboard con sus workflows activos
  - Crear nuevos workflows con validación de fechas
  - Ver detalle completo de un workflow
  - Solicitar línea base, revisión RM, informe diff, y pruebas QA según el estado
  - Agregar y ver el plan de pruebas
  - Ver historial completo de actividades con comentarios

✓ La máquina de estados funciona correctamente:
  - Botones se habilitan/deshabilitan según condiciones
  - Actividades se crean con datos correctos
  - Estados de workflow progresan según el flujo

✓ El código sigue las buenas prácticas Django:
  - Sin queries N+1
  - Validaciones en el lugar correcto
  - Templates limpios y mantenibles
  - Permisos validados correctamente

✓ El rol "Administrador" mantiene su vista original sin cambios
</success_criteria>

<notes>
- Esta implementación es solo para el rol "Jefe de Proyecto". Los otros roles (SCM, Release Manager, QA) quedan pendientes para futuras iteraciones.
- La lógica de estados es compleja - considera crear un diagrama de estados para documentación.
- Los correlativos deben manejarse cuidadosamente para evitar race conditions si hay concurrencia.
- Considera agregar índices de base de datos en campos frecuentemente consultados (jefe_proyecto, estado_workflow).
</notes>
