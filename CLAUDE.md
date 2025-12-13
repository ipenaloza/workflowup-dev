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
   - **Other Roles:** Workflow + Password Change + Logout
   - Links include `url`, `text`, and `name` keys for template rendering

### URL Structure

```
/                    → Login page (root)
/logout/             → Logout
/password-change/    → Password change (all authenticated)
/password-reset/     → Password reset flow (4 views)
/usuarios/           → User administration (admin only)
/workflow/           → Workflow dashboard (all authenticated)
/admin/              → Django admin site
```

### Apps

**users_admin** - User Management
- Custom User model with RBAC
- CRUD operations (admin role only via `@admin_required`)
- User list with search/filter/pagination
- Forms: `UserCreateForm` (with password fields), `UserUpdateForm` (role + is_active only)
- Soft delete protection

**workflow** - Workflow System
- Dashboard accessible to all authenticated users
- Displays user info and role
- Placeholder for future workflow features

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

### Adding New Roles

1. Update `User.ROLE_CHOICES` in `users_admin/models.py`
2. Create migration: `python workflowup/manage.py makemigrations`
3. Apply migration: `python workflowup/manage.py migrate`
4. Update `context_processors.py` for role-based navigation if needed
5. Create custom decorators like `@admin_required` for new role-specific access control

### Database Workflow (Development)

1. Make model changes
2. `python workflowup/manage.py makemigrations`
3. Review migration files in `*/migrations/`
4. `python workflowup/manage.py migrate`
5. If needed, reset: `python reset_db.py && python workflowup/manage.py migrate && python setup_users.py`

### Test Accounts

Default test accounts (created by `setup_users.py`):
- **admin/admin123** - Administrador role
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
