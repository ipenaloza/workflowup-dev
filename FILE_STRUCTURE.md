# WorkflowUp - Complete File Structure

## Project Root

```
workflowup2/
├── README.md                           # Main project documentation
├── QUICK_START.md                      # Quick start guide
├── IMPLEMENTATION_SUMMARY.md           # Technical documentation
├── TESTING_GUIDE.md                    # Testing checklist
├── FILE_STRUCTURE.md                   # This file
├── CLAUDE.md                           # Project overview for developers
│
├── reset_db.py                         # Database reset utility script
├── setup_users.py                      # Test user creation script
├── requirements.txt                    # Python dependencies
│
├── py-env/                             # Python virtual environment
│   └── ... (virtual environment files)
│
└── workflowup/                         # Django project root
    ├── manage.py                       # Django management script
    │
    ├── templates/                      # Global template directory
    │   ├── base.html                   # Master template (header, footer, Tailwind)
    │   ├── base_authenticated.html     # Base with navigation
    │   ├── base_anonymous.html         # Base without navigation
    │   │
    │   ├── registration/               # Authentication templates
    │   │   ├── login.html              # Login page
    │   │   ├── password_change_form.html
    │   │   ├── password_change_done.html
    │   │   ├── password_reset_form.html
    │   │   ├── password_reset_done.html
    │   │   ├── password_reset_confirm.html
    │   │   ├── password_reset_complete.html
    │   │   └── password_reset_email.html
    │   │
    │   ├── users_admin/                # User administration templates
    │   │   ├── user_list.html          # User list with search/filter
    │   │   └── user_form.html          # Create/update user form
    │   │
    │   └── workflow/                   # Workflow templates
    │       └── dashboard.html          # Workflow dashboard
    │
    ├── users_admin/                    # User administration app
    │   ├── __init__.py
    │   ├── admin.py                    # Django admin configuration
    │   ├── apps.py                     # App configuration
    │   ├── context_processors.py       # Navigation context processor
    │   ├── decorators.py               # @admin_required decorator
    │   ├── forms.py                    # UserCreateForm, UserUpdateForm
    │   ├── models.py                   # Custom User model
    │   ├── tests.py                    # Unit tests (to be implemented)
    │   ├── urls.py                     # User admin URL patterns
    │   ├── views.py                    # User CRUD views
    │   │
    │   └── migrations/                 # Database migrations
    │       ├── __init__.py
    │       └── 0001_initial.py         # Initial user model migration
    │
    ├── workflow/                       # Workflow app
    │   ├── __init__.py
    │   ├── admin.py                    # Django admin configuration
    │   ├── apps.py                     # App configuration
    │   ├── models.py                   # Workflow models (empty for now)
    │   ├── tests.py                    # Unit tests (to be implemented)
    │   ├── urls.py                     # Workflow URL patterns
    │   ├── views.py                    # Dashboard view
    │   │
    │   └── migrations/                 # Database migrations
    │       └── __init__.py
    │
    └── workflowup/                     # Settings package
        ├── __init__.py
        ├── asgi.py                     # ASGI configuration
        ├── settings.py                 # Django settings
        ├── urls.py                     # Root URL configuration
        └── wsgi.py                     # WSGI configuration
```

## File Descriptions

### Root Level Documentation

| File | Purpose | Audience |
|------|---------|----------|
| README.md | Main project overview and documentation | All users |
| QUICK_START.md | Get started quickly with test accounts | New users |
| IMPLEMENTATION_SUMMARY.md | Complete technical documentation | Developers |
| TESTING_GUIDE.md | Comprehensive testing checklist | QA/Testers |
| FILE_STRUCTURE.md | This file - visual file tree | All users |
| CLAUDE.md | Development commands and structure | Developers |

### Utility Scripts

| File | Purpose | Usage |
|------|---------|-------|
| reset_db.py | Drop and recreate MySQL database | `python reset_db.py` |
| setup_users.py | Create test users with all roles | `python setup_users.py` |
| requirements.txt | Python package dependencies | `pip install -r requirements.txt` |

### Django Project Files

#### manage.py
Django management script for running commands like `runserver`, `migrate`, etc.

#### templates/

**Base Templates:**
- `base.html` - Master template with header, footer, Tailwind CSS
- `base_authenticated.html` - Extends base, adds navigation
- `base_anonymous.html` - Extends base, no navigation

**registration/ (Authentication):**
All Django auth views templates with custom styling

**users_admin/ (User Management):**
- `user_list.html` - Paginated user list with search/filter
- `user_form.html` - Reusable form for create/update

**workflow/ (Dashboard):**
- `dashboard.html` - Main workflow dashboard

#### users_admin/ App

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| models.py | Custom User model | User (extends AbstractUser) |
| views.py | User CRUD views | UserListView, UserCreateView, UserUpdateView |
| forms.py | User forms | UserCreateForm, UserUpdateForm |
| urls.py | URL routing | user_list, user_create, user_update |
| admin.py | Django admin config | UserAdmin |
| decorators.py | Access control | @admin_required |
| context_processors.py | Navigation | navigation_context() |

#### workflow/ App

| File | Purpose | Key Functions |
|------|---------|---------------|
| views.py | Dashboard view | dashboard() |
| urls.py | URL routing | dashboard |
| models.py | Future models | (empty) |

#### workflowup/ Package

| File | Purpose | Key Settings |
|------|---------|--------------|
| settings.py | Django configuration | AUTH_USER_MODEL, DATABASES, TEMPLATES |
| urls.py | Root URL config | All URL patterns |
| wsgi.py | WSGI config | Production deployment |
| asgi.py | ASGI config | Async support |

## File Relationships

### Template Inheritance

```
base.html
├── base_authenticated.html
│   ├── users_admin/user_list.html
│   ├── users_admin/user_form.html
│   ├── workflow/dashboard.html
│   ├── registration/password_change_form.html
│   └── registration/password_change_done.html
│
└── base_anonymous.html
    ├── registration/login.html
    ├── registration/password_reset_form.html
    ├── registration/password_reset_done.html
    ├── registration/password_reset_confirm.html
    └── registration/password_reset_complete.html
```

### URL Routing Flow

```
workflowup/urls.py (root)
├── / → LoginView
├── /logout/ → LogoutView
├── /password-change/ → PasswordChangeView
├── /password-reset/ → PasswordResetView
├── /usuarios/ → include(users_admin.urls)
│   ├── /usuarios/ → UserListView
│   ├── /usuarios/crear/ → UserCreateView
│   └── /usuarios/<id>/editar/ → UserUpdateView
├── /workflow/ → include(workflow.urls)
│   └── /workflow/ → dashboard
└── /admin/ → admin.site.urls
```

### Import Dependencies

```
users_admin/views.py
├── imports models.py → User model
├── imports forms.py → UserCreateForm, UserUpdateForm
└── used by urls.py

users_admin/forms.py
├── imports models.py → User model
└── used by views.py

users_admin/context_processors.py
└── registered in settings.py → TEMPLATES['OPTIONS']['context_processors']

workflow/views.py
└── used by workflow/urls.py
```

## Database Schema Files

### Migration Files

```
users_admin/migrations/
└── 0001_initial.py          # Creates users_admin_user table
                             # with all AbstractUser fields + role

workflow/migrations/
└── (no migrations yet)      # Will contain workflow model migrations
```

## Configuration Files

### settings.py Structure

```python
# Key configurations in settings.py:

BASE_DIR                      # Project root path
SECRET_KEY                    # Django secret (should be in env var for production)
DEBUG = True                  # Set to False in production
ALLOWED_HOSTS = []            # Add domains in production

INSTALLED_APPS = [
    # Django apps...
    'users_admin',            # Custom user management
    'workflow',               # Workflow application
]

TEMPLATES = [
    'DIRS': [BASE_DIR / 'templates'],
    'OPTIONS': {
        'context_processors': [
            # ...
            'users_admin.context_processors.navigation_context',
        ],
    },
]

AUTH_USER_MODEL = 'users_admin.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'workflow:dashboard'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## File Sizes (Approximate)

| File | Lines | Size | Complexity |
|------|-------|------|------------|
| models.py (User) | 65 | 2 KB | Medium |
| views.py (users_admin) | 116 | 4 KB | Medium |
| forms.py | 70 | 2 KB | Low |
| user_list.html | 165 | 6 KB | Medium |
| user_form.html | 125 | 5 KB | Medium |
| dashboard.html | 80 | 3 KB | Low |
| base.html | 50 | 2 KB | Low |

## Access Patterns

### Who Can Access What?

```
Public (Not logged in):
├── /                          (login page)
└── /password-reset/*          (all password reset views)

Authenticated Users (All roles):
├── /workflow/                 (dashboard)
├── /password-change/          (change own password)
└── /logout/                   (logout)

Administrador Role Only:
└── /usuarios/*                (all user management)

Superusers Only:
└── /admin/*                   (Django admin interface)
```

## Development Workflow Files

### Files You'll Edit Most

1. **Adding features:**
   - `workflow/views.py` - Add workflow views
   - `workflow/models.py` - Add workflow models
   - `workflow/urls.py` - Add workflow URLs
   - `templates/workflow/` - Add workflow templates

2. **Modifying user management:**
   - `users_admin/views.py` - Change user views
   - `users_admin/forms.py` - Modify user forms
   - `templates/users_admin/` - Update templates

3. **Styling changes:**
   - `templates/base.html` - Modify header/footer
   - Individual templates - Update specific pages

4. **Configuration:**
   - `workflowup/settings.py` - Django settings
   - `workflowup/urls.py` - Root URL patterns

### Files You Shouldn't Edit

- `migrations/*.py` - Generated by Django
- `py-env/` - Virtual environment files
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python files

## Next Steps

Now that you understand the file structure:

1. **Start the server:** See QUICK_START.md
2. **Test the system:** See TESTING_GUIDE.md
3. **Understand the code:** See IMPLEMENTATION_SUMMARY.md
4. **Add features:** Modify workflow app files

Happy coding!
