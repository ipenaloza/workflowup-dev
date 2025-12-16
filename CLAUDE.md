# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WorkflowUp is a Django 5.2.8 web application implementing **role-based access control (RBAC)** for project and workflow management. The application features a custom user model with 5 distinct roles, user administration capabilities, and role-specific navigation.

**Key Technologies:**
- Python 3.13 (virtual environment in `py-env/`)
- Django 5.2.8
- MySQL 8.0 (database: `workflowup2`, credentials: `admindb`/`admindb`)
- Tailwind CSS (CDN)

## Project Structure

```
workflowup2/
├── py-env/                          # Python 3.13 virtual environment
├── requirements.txt                 # Project dependencies
├── reset_db.py                      # Database reset utility
├── setup_users.py                   # Test user creation script
└── workflowup/                      # Django project root
    ├── manage.py                    # Django CLI (NOTE: not at repo root!)
    ├── templates/                   # Global templates (auth, base)
    ├── users_admin/                 # User administration app
    │   ├── models.py               # Custom User model
    │   ├── decorators.py           # @admin_required decorator
    │   ├── context_processors.py   # Role-based navigation
    │   ├── forms.py                # User creation/edit forms
    │   └── views.py                # CRUD views (admin only)
    ├── workflow/                    # Workflow app
    │   └── views.py                # Dashboard (all users)
    └── workflowup/                  # Django settings package
        ├── settings.py             # Main configuration
        └── urls.py                 # Root URL routing
```

## Development Commands

**CRITICAL:** `manage.py` is located at `workflowup/manage.py`, NOT at the project root. Always run Django commands from the project root as `python workflowup/manage.py <command>`.

### Environment Setup
```bash
# Activate virtual environment
source py-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Run development server (from project root)
python workflowup/manage.py runserver

# Run on specific port
python workflowup/manage.py runserver 8080
```

### Database Operations
```bash
# Create migrations
python workflowup/manage.py makemigrations

# Apply migrations
python workflowup/manage.py migrate

# Create superuser
python workflowup/manage.py createsuperuser

# Django shell
python workflowup/manage.py shell

# Reset database (development only - drops and recreates all tables)
python reset_db.py
python workflowup/manage.py migrate
python setup_users.py
```

### Testing
```bash
# Run all tests
python workflowup/manage.py test

# Run tests for specific app
python workflowup/manage.py test users_admin
python workflowup/manage.py test workflow

# Run specific test case
python workflowup/manage.py test users_admin.tests.TestClassName.test_method_name

# Check for issues (validates models, settings, etc.)
python workflowup/manage.py check
```

## Architecture

### Custom User Model (`users_admin.User`)
- Extends Django's `AbstractUser`
- **5 Roles:** Administrador, Jefe de Proyecto, SCM, Release Manager, QA
- **Username Rules:**
  - Only lowercase letters (a-z), automatically converted to lowercase on save
  - Validated via `RegexValidator` in model and forms
- **Email:** Unique and required
- **Names:** First and last name required (unlike base AbstractUser)
- **Soft Delete:** Physical deletion prevented via overridden `delete()` method - raises Exception. Use `is_active=False` instead
- **Location:** `workflowup/users_admin/models.py`

### Role-Based Access Control (RBAC)

**Two-Level Access System:**

1. **@admin_required Decorator** (`users_admin/decorators.py`)
   - Restricts views to users with `role == 'Administrador'`
   - Combines `@login_required` with role check
   - Applied to all user administration CRUD views
   - Raises `PermissionDenied` for non-admin users

2. **Context Processor Navigation** (`users_admin/context_processors.py`)
   - Dynamically generates `nav_links` in template context based on user role
   - Registered in `settings.py` TEMPLATES context_processors as `users_admin.context_processors.navigation_context`
   - **Administrador:** User Admin + Workflow + Password Change + Logout
   - **Jefe de Proyecto:** Workflow + Create Workflow + Password Change + Logout
   - **Other Roles:** Workflow + Password Change + Logout
   - Links include `url`, `text`, and `name` keys for template rendering

### URL Structure

```
/                                                    → Login page (root)
/logout/                                             → Logout
/password-change/                                    → Password change (all authenticated)
/password-reset/                                     → Password reset flow (4 views)
/usuarios/                                           → User administration (admin only)
/workflow/                                           → Workflow dashboard (role-specific views)
/workflow/create/                                    → Create workflow (Jefe de Proyecto only)
/workflow/<id>/                                      → Workflow detail (Jefe de Proyecto)
/workflow/<id>/plan-pruebas/                         → QA test plan (Jefe de Proyecto)
/workflow/<id>/scm/                                  → SCM workflow detail (SCM role only)
/workflow/<id>/rm/                                   → RM workflow detail (Release Manager only)
/workflow/<id>/qa/                                   → QA workflow detail (QA role only)
/workflow/<id>/qa/<id_prueba>/update-avance/         → AJAX: Update test progress
/workflow/<id>/qa/<id_prueba>/toggle-rechazar/       → AJAX: Toggle test rejection
/admin/                                              → Django admin site
```

### Apps

**users_admin** - User Management
- Custom User model with RBAC
- CRUD operations (admin role only via `@admin_required`)
- User list with search/filter/pagination
- Forms: `UserCreateForm` (with password fields), `UserUpdateForm` (role + is_active only)
- Soft delete protection

**workflow** - Workflow System
- **Role-specific dashboards:** Different views for Jefe de Proyecto, SCM, and other roles
- **Workflow CRUD:** Create and manage software release workflows (Jefe de Proyecto only)
- **Activity Tracking:** Comprehensive audit log via `Actividad` model with workflow states and process transitions
- **Process Flow:** Sequential approval workflow (línea base → RM Rev → Diff Info → QA)
- **QA Test Plans:** Test management with results tracking (`PlanPruebaQA` model)
- **SCM Integration:** Dedicated SCM view for baseline approval and diff reports

### Workflow System Architecture

The workflow app implements a **sequential approval process** for software release management:

**Data Models:**
1. **Workflow** - Main workflow entity with project info, dates, release info, and baseline tracking
2. **Actividad** - Immutable activity log tracking all state changes and process transitions
3. **PlanPruebaQA** - QA test plan with progress and results

**Workflow States** (`estado_workflow` field in Actividad):
- **Nuevo** - Initial state after creation
- **Activo** - Active workflow with ongoing processes
- **Cancelado** - Cancelled by Jefe de Proyecto
- **Cerrado** - Completed workflow (all processes approved)

**Process Flow** (sequential approval chain via `proceso` field):
1. **linea base** - SCM creates baseline (SCM role)
2. **RM Rev** - Release Manager review
3. **Diff Info** - SCM generates diff report (SCM role)
4. **QA** - Quality Assurance testing (QA role)

**Process States** (`estado_proceso` field):
- **En Proceso** - Awaiting approval from assigned role
- **Ok** - Approved, can proceed to next process
- **No Ok** - Rejected, Jefe de Proyecto must re-request

**Key Model Methods** (`workflowup/workflow/models.py:53-71`):
- `get_actividad_workflow()` - Latest overall activity (determines workflow state)
- `get_actividad_scm1()`, `get_actividad_rm()`, `get_actividad_scm2()`, `get_actividad_qa()` - Latest activity for each process
- These methods drive button enabling/disabling logic in views

**Role-Based Views:**
- **Jefe de Proyecto**: Create workflows, request processes, manage test plans (`dashboard_jp.html`, `workflow_detail.html`, `plan_pruebas.html`)
- **SCM**: Approve/reject línea base and Diff Info requests (`dashboard_scm.html`, `workflow_detail_scm.html`)
- **Release Manager**: Approve/reject RM Rev requests (`dashboard_rm.html`, `workflow_detail_rm.html`)
- **QA**: Execute tests, approve/reject QA process (`dashboard_qa.html`, `workflow_detail_qa.html`)
- **Administrador**: Generic dashboard (`dashboard.html`)

**Business Rules:**
- Processes must be requested sequentially (línea base → RM Rev → Diff Info → QA)
- **SCM** must populate `workflow.linea_base` field before approving línea base process
- **Release Manager** must populate `workflow.codigo_rm` field before approving RM Rev process
- Jefe de Proyecto must populate `workflow.release` field before requesting RM Rev
- Comments are **mandatory** when rejecting (estado_proceso='No Ok'), optional for approvals
- Activities are immutable - create new activity for state changes, never update existing
- Rejections allow re-requests (process state can cycle between 'En Proceso' and 'No Ok')

### Key Settings

- **Custom User Model:** `AUTH_USER_MODEL = 'users_admin.User'`
- **Login Redirects:** `LOGIN_REDIRECT_URL = 'workflow:dashboard'`, `LOGIN_URL = 'login'`
- **Email Backend:** Console backend (development) - password reset emails print to terminal
- **Templates:** Global templates in `workflowup/templates/`
- **Database:** MySQL at 127.0.0.1:3306, database `workflowup2`
- **Context Processor:** `users_admin.context_processors.navigation_context` provides role-based navigation

## Common Development Tasks

### Working with the Custom User Model

```python
# In views/models, always use:
from django.contrib.auth import get_user_model
User = get_user_model()

# Or import directly:
from users_admin.models import User

# Check user role:
if request.user.role == 'Administrador':
    # Admin-specific logic
    pass
```

### Working with Workflows

```python
# Creating a new activity (always increment id_actividad)
from django.db.models import Max

max_id = workflow.actividades.aggregate(Max('id_actividad'))['id_actividad__max']
next_id = (max_id or 0) + 1

Actividad.objects.create(
    workflow=workflow,
    id_actividad=next_id,
    usuario=request.user.username,
    estado_workflow='Activo',
    proceso='linea base',
    estado_proceso='En Proceso',
    actividad='Linea base solicitada',
    comentario=comentario_opcional
)

# Checking workflow state before actions
actividad_scm1 = workflow.get_actividad_scm1()
if actividad_scm1 and actividad_scm1.estado_proceso == 'Ok':
    # SCM has approved, can proceed to next step
    pass

# Button enabling logic (see workflow/views.py:376-423)
# Complex conditional logic based on previous approvals and current state
# Example for RM Rev button:
btn2_enabled = (
    workflow.release and  # Release field must be populated
    (
        (actividad_scm1 and actividad_scm1.estado_proceso == 'Ok') or  # SCM approved
        (actividad_rm and actividad_rm.estado_proceso == 'No Ok')      # RM rejected (re-request)
    ) and not (actividad_rm and actividad_rm.estado_proceso == 'Ok')  # Not already approved
)
```

### Adding New Roles

1. Update `User.ROLE_CHOICES` in `users_admin/models.py`
2. Create migration: `python workflowup/manage.py makemigrations`
3. Apply migration: `python workflowup/manage.py migrate`
4. Update `context_processors.py` for role-based navigation if needed
5. Create custom decorators like `@admin_required` for new role-specific access control

### Adding New Workflow Processes

1. Add process to `Actividad.PROCESO_CHOICES` in `workflow/models.py`
2. Create `get_actividad_<process>()` helper method in `Workflow` model
3. Add button logic in Jefe de Proyecto view (`workflow_detail`)
4. Create role-specific view for approval (like `workflow_detail_scm`)
5. Update dashboard filters to include new process
6. Create migration and apply

### Database Workflow (Development)

1. Make model changes
2. `python workflowup/manage.py makemigrations`
3. Review migration files in `*/migrations/`
4. `python workflowup/manage.py migrate`
5. If needed, reset: `python reset_db.py && python workflowup/manage.py migrate && python setup_users.py`

### Test Accounts

Default test accounts (created by `setup_users.py`):
- **admin/admin123** - Administrador role
- **jproyecto/test123** - Jefe de Proyecto role
- **scm_user/test123** - SCM role
- **release_mgr/test123** - Release Manager role
- **qa_tester/test123** - QA role
- See `QUICK_START.md` for full list

## Important Notes

- **manage.py Location:** Always run Django commands from project root as `python workflowup/manage.py <command>`
- **Usernames:** Automatically converted to lowercase on save, validated to contain only letters (a-z)
- **User Deletion:** Physically prevented via overridden `delete()` method - always use `is_active=False` to deactivate
- **Email:** Console backend in development - check terminal output for password reset emails
- **MySQL Required:** Ensure MySQL server running on 127.0.0.1:3306 before starting application
- **Settings Module:** `workflowup.settings`
- **Root URLconf:** `workflowup.urls`
- **Activity Immutability:** Activities are immutable audit logs - never update/delete, always create new activities
- **Sequential Process Flow:** Workflows enforce sequential approval (línea base → RM Rev → Diff Info → QA)
- **Mandatory Comments:** Rejections (estado_proceso='No Ok') require comments; approvals are optional
- **SCM Baseline Requirement:** SCM must populate `workflow.linea_base` field before approving línea base process
- **RM Code Requirement:** Release Manager must populate `workflow.codigo_rm` field before approving RM Rev process
- **Release Field Requirement:** Jefe de Proyecto must populate `workflow.release` field before requesting RM Rev

## Security Features

- CSRF protection on all forms
- Password hashing (PBKDF2 via Django defaults)
- XSS prevention (template auto-escaping)
- SQL injection prevention (Django ORM)
- Session-based authentication
- Login required decorators
- Role-based access control via decorators and context processors

## Documentation Files

- **README.md** - Comprehensive project documentation with features, tech stack, and deployment
- **QUICK_START.md** - Getting started guide with test accounts and basic navigation
- **IMPLEMENTATION_SUMMARY.md** - Detailed technical architecture and design decisions
- **TESTING_GUIDE.md** - QA testing checklist with test scenarios
- **CLAUDE.md** - This file
