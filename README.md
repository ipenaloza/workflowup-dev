# WorkflowUp - Django Role-Based Access Control System

A comprehensive Django 5.2.8 web application implementing role-based access control (RBAC) for project and workflow management. Features custom user authentication, user administration, and role-specific access controls.

## Features

- **Custom User Model** with 5 distinct roles
- **User Administration** module (admin-only access)
- **Role-Based Navigation** (dynamic based on user role)
- **Complete Authentication** (login, logout, password change, password reset)
- **Workflow Dashboard** (all authenticated users)
- **Responsive UI** with Tailwind CSS
- **Security Features** (CSRF, XSS protection, password hashing)
- **Soft Delete** (users can be deactivated, not deleted)

## User Roles

1. **Administrador** - Full system access including user management
2. **Jefe de Proyecto** - Project management capabilities
3. **SCM** - Software Configuration Management
4. **Release Manager** - Release management
5. **QA** - Quality Assurance

## Quick Start

### Prerequisites

- Python 3.13
- MySQL 8.0+
- Virtual environment (already set up in `py-env/`)

### Start the Application

```bash
# Navigate to project directory
cd /Users/ipenaloza/WorkflowUp/@_version_2/workflowup2/workflowup

# Run the development server
python manage.py runserver
```

Open your browser: **http://127.0.0.1:8000/**

### Test Accounts

| Username | Password | Role | Access |
|----------|----------|------|--------|
| admin | admin123 | Administrador | User Admin + Workflow |
| qa_tester | test123 | QA | Workflow only |

See **QUICK_START.md** for more test accounts and detailed usage.

## Documentation

This project includes comprehensive documentation:

### 1. QUICK_START.md
- **Purpose:** Get up and running in minutes
- **Contents:** Login credentials, basic navigation, quick tests
- **Audience:** First-time users

### 2. IMPLEMENTATION_SUMMARY.md
- **Purpose:** Understand the architecture and design
- **Contents:** Complete technical documentation, file structure, design decisions
- **Audience:** Developers, maintainers

### 3. TESTING_GUIDE.md
- **Purpose:** Comprehensive testing checklist
- **Contents:** All test scenarios, verification steps, edge cases
- **Audience:** QA testers, developers

### 4. CLAUDE.md
- **Purpose:** Project overview and development commands
- **Contents:** Structure, dependencies, common operations
- **Audience:** Developers

## Project Structure

```
workflowup2/
├── README.md                        # This file
├── QUICK_START.md                   # Quick start guide
├── IMPLEMENTATION_SUMMARY.md        # Technical documentation
├── TESTING_GUIDE.md                 # Testing checklist
├── CLAUDE.md                        # Project overview
├── reset_db.py                      # Database reset utility
├── setup_users.py                   # Test user creation
├── py-env/                          # Virtual environment
└── workflowup/                      # Django project
    ├── manage.py
    ├── templates/                   # Global templates
    ├── users_admin/                 # User administration app
    ├── workflow/                    # Workflow app
    └── workflowup/                  # Settings package
```

## Technology Stack

- **Backend:** Django 5.2.8
- **Database:** MySQL 8.0
- **Python:** 3.13
- **Frontend:** HTML5, Tailwind CSS (CDN)
- **Authentication:** Django built-in auth system

## Key Features Details

### Custom User Model
- Extends Django's `AbstractUser`
- Additional `role` field with 5 choices
- Unique email constraint
- Required first/last name
- Soft delete protection

### User Administration
- **List View:** Search, filter, pagination
- **Create View:** Full user creation with validation
- **Update View:** Edit role and active status only
- **No Delete:** Physical deletion prevented
- **Access Control:** Admin role required

### Authentication System
- Login at root URL (`/`)
- Session-based authentication
- Password change for authenticated users
- Email-based password reset
- Console email backend (development)

### Workflow Application
- Main dashboard after login
- Shows user name and role
- Accessible to all authenticated users
- Placeholder for future features

### Role-Based Navigation
- **Administrador:** User Admin + Workflow + Password Change
- **Other Roles:** Workflow + Password Change
- Dynamic based on user role
- Implemented via context processor

### Security Features
- CSRF protection on all forms
- Password hashing (PBKDF2)
- XSS prevention (auto-escaping)
- SQL injection prevention (ORM)
- Session management
- Login required decorators

## Development

### Common Commands

```bash
# Create migrations
python workflowup/manage.py makemigrations

# Apply migrations
python workflowup/manage.py migrate

# Create superuser
python workflowup/manage.py createsuperuser

# Django shell
python workflowup/manage.py shell

# Run tests
python workflowup/manage.py test

# Check for issues
python workflowup/manage.py check
```

### Database Reset

If you need to reset the database:

```bash
python reset_db.py
python workflowup/manage.py migrate
python setup_users.py
```

## URLs

- **Root:** `/` - Login page
- **Logout:** `/logout/`
- **Password Change:** `/password-change/`
- **Password Reset:** `/password-reset/`
- **User Admin:** `/usuarios/` (admin only)
- **Workflow:** `/workflow/`
- **Django Admin:** `/admin/`

## Testing

See **TESTING_GUIDE.md** for comprehensive testing checklist including:

- Authentication flow tests
- Authorization tests (role-based)
- User CRUD operations
- Password management
- UI/UX verification
- Security testing
- Edge cases

## Configuration

### Database

```python
# workflowup/workflowup/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'workflowup2',
        'USER': 'admindb',
        'PASSWORD': 'admindb',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    }
}
```

### Email (Development)

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Password reset emails print to terminal during development.

## Screenshots

### Login Page
- Blue header with "WorkflowUp"
- Login form (username/password)
- "Forgot password" link

### User Administration (Admin Only)
- User list with search and filters
- Create/edit user forms
- Role and status management

### Workflow Dashboard
- User name and role display
- Navigation based on role
- Placeholder for workflow features

## Known Limitations

1. No user profile editing (users can't update their own info)
2. No email verification on user creation
3. Basic password requirements (Django defaults)
4. No account lockout after failed attempts
5. No audit logging
6. Console email backend (development only)

## Future Enhancements

### Short-term
- User profile editing
- Admin dashboard with statistics
- Audit logging for user changes
- Better error handling

### Long-term
- Email verification
- Two-factor authentication
- API endpoints
- Advanced role permissions
- Workflow-specific features

## Production Deployment

Before deploying to production:

1. **Security**
   - Change SECRET_KEY
   - Set DEBUG = False
   - Configure ALLOWED_HOSTS
   - Use environment variables for secrets

2. **Email**
   - Configure SMTP settings
   - Test email delivery

3. **Database**
   - Use production database
   - Set up automated backups

4. **Static Files**
   - Run collectstatic
   - Configure web server

5. **Monitoring**
   - Set up error logging
   - Configure application monitoring

See **IMPLEMENTATION_SUMMARY.md** for complete deployment checklist.

## Support

### Documentation
- **QUICK_START.md** - Quick start guide
- **IMPLEMENTATION_SUMMARY.md** - Technical documentation
- **TESTING_GUIDE.md** - Testing checklist
- **CLAUDE.md** - Project overview

### Common Issues

**Can't login:** Check username/password, verify user is active

**Permission denied:** Verify user has correct role (Administrador for user admin)

**Templates not found:** Check TEMPLATES DIRS in settings.py

**Database errors:** Run `python reset_db.py` and migrate again

## Credits

- **Developer:** Iván Peñaloza
- **Institution:** Universidad Andrés Bello
- **Project Type:** Proyecto de título
- **Year:** 2025
- **Framework:** Django 5.2.8

## License

Educational/Academic Use

## Contact

For questions or issues related to this project:
- Email: i.pealozazamora@uandresbello.edu

---

**Start using WorkflowUp today!** See QUICK_START.md to get started.
