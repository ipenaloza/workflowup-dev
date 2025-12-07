<objective>
Create a complete Django role-based access control (RBAC) system with two apps:
1. **User Administration App**: Custom user management with role assignment, activation/deactivation, and admin-only access
2. **Workflow App**: Main application area with role-based navigation and authenticated access

This system will serve as the foundation for a project management application where different user roles (Administrator, Project Manager, SCM, Release Manager, QA) have different permissions and access levels. The authentication system must be secure, use Django's built-in auth components optimally, and provide password recovery functionality.
</objective>

<context>
This is a Django 5.2.8 project using MySQL backend. The project structure has Django at `workflowup/` with `manage.py` located at `workflowup/manage.py`. Review @workflowup/workflowup/settings.py to understand the current configuration.

The system needs to handle user authentication, authorization, and management for a workflow/project management system. Users will authenticate with usernames, have specific roles, and access different parts of the application based on their assigned role.
</context>

<requirements>

## User Model Requirements

1. **Extend Django's AbstractUser** to create a custom user model with an additional `role` field
2. **Role choices** must be exactly: "Administrador", "Jefe de Proyecto", "SCM", "Release Manager", "QA"
3. **Unique constraints**:
   - `username` must be unique (used for authentication)
   - `email` must be unique across all users
4. **Soft delete only**: Users can be activated/deactivated using Django's built-in `is_active` field, but NEVER physically deleted from database
5. **Required fields**: username, first_name (Nombre), last_name (Apellido), email, role, is_active

## User Administration App ("users_admin" or similar)

1. **Access control**: Only users with role="Administrador" can access this module
2. **CRUD operations**:
   - **Create**: Add new users with all required fields
   - **Read**: Display list of all users showing: Username, Nombre, Apellido, Email, Rol, Active status
   - **Update**: Allow modification of ONLY `role` and `is_active` fields
   - **No Delete**: Physical deletion must be prevented; only deactivation allowed
3. **Validation**:
   - Prevent duplicate usernames (database constraint + form validation)
   - Prevent duplicate emails (database constraint + form validation)
4. **Password management**:
   - Use Django's built-in password change views and forms
   - Provide password change functionality accessible from navigation
5. **Password recovery**:
   - Implement Django's password reset functionality with email verification
   - Configure password reset views and email backend

## Workflow App

1. **Main view**: After successful login, redirect users to the workflow app
2. **Authentication required**: All workflow views require login; unauthenticated users redirected to login page
3. **Initial content**: Display "Listado de Workflow de: [first_name] [last_name] ([role])"
4. **Future expansion**: This app will hold the main workflow/project management features

## Authentication & Authorization

1. **Login view**: Root URL ("/") should display the login page
2. **Authentication**: Use Django's built-in authentication system with `username` as the identifier
3. **Session management**: Use Django's session framework for maintaining logged-in state
4. **Authorization**: Role-based access control using decorators or mixins
5. **Password recovery**: Complete forgot-password flow with email token verification
6. **Security**: Implement CSRF protection, secure password hashing (Django default), and login throttling if possible

## UI/UX Requirements

### Header (All Pages)
- **Login page**: Blue background, white text, left-aligned text "WorkflowUp"
- **Authenticated pages**: Blue background, white text
  - Left side: "WorkflowUp"
  - Right side: "[first_name] [last_name] ([role])"

### Navigation Bar (Authenticated Pages Only)
- **Administrator role**: Links to User Administration, Workflow, Change Password
- **All other roles**: Links to Workflow, Change Password
- Navigation bar appears below the header

### Footer (All Pages)
- Blue background, white text, centered
- Text: "2025 - Proyecto de titulo de Iván Peñaloza (i.pealozazamora@uandresbello.edu)"

### Body Styling
- Light gray background color for all page bodies

### Styling Framework
- **Use Tailwind CSS** for all styling throughout the application
- Apply utility classes directly in HTML templates
- Use responsive utilities for mobile-friendly layouts

</requirements>

<implementation>

## Step-by-Step Implementation Plan

### 1. Create Custom User Model (users_admin app)

- Create app: `python workflowup/manage.py startapp users_admin`
- Define custom user model extending `AbstractUser` with `role` field
- Add role choices as model constants
- Set unique constraints on username and email
- Update `settings.py` with `AUTH_USER_MODEL = 'users_admin.User'`
- Create and run migrations BEFORE creating any users

**Why this approach**: Django requires AUTH_USER_MODEL to be set before first migration. Extending AbstractUser gives us all Django auth functionality plus our custom role field. Using database constraints ensures data integrity at the lowest level.

### 2. Configure Authentication URLs

- Update `workflowup/urls.py` to include:
  - Login view at root ("/")
  - Logout view
  - Password change views (Django built-in)
  - Password reset views (Django built-in) with email configuration
  - User admin app URLs (for admin users only)
  - Workflow app URLs

**Why**: Centralized URL configuration makes the authentication flow clear and maintainable. Django's built-in views handle security best practices automatically.

### 3. Create User Administration Views

- **ListView**: Display all users with filtering/search capabilities
- **CreateView**: Form to add new users (set initial password, force change on first login)
- **UpdateView**: Form to edit ONLY role and is_active fields
- **Delete prevention**: Override delete methods to raise exceptions or disable delete buttons entirely
- **Access control**: Use `@login_required` + custom decorator/mixin to check role="Administrador"

**Why role-only editing**: Username changes would break authentication; email changes need verification; name changes should be user-initiated. Only administrators should control roles and account status.

### 4. Create Workflow App

- Create app: `python workflowup/manage.py startapp workflow`
- Create main view that displays user info and role
- Apply `@login_required` decorator to all views
- Set `LOGIN_URL` in settings.py to redirect to login page

**Why**: Separating workflow into its own app keeps concerns separated and allows for future expansion without cluttering the user admin app.

### 5. Create Base Templates

- **base.html**: Master template with header, footer, navigation (conditional on user role), and body block
- **login.html**: Login form (username/password) extending base but hiding navigation
- **password_change.html**: Password change form
- **password_reset.html**: Password reset request form
- **password_reset_confirm.html**: New password entry form
- **user_admin templates**: List, create, update forms for user management
- **workflow templates**: Main workflow dashboard

**Template inheritance structure**:
```
base.html (header, footer, styling)
├── base_authenticated.html (adds navigation based on role)
│   ├── workflow templates
│   └── user_admin templates
└── base_anonymous.html (login, password reset - no navigation)
```

**Why template inheritance**: Avoids repetition of header/footer/styling. Role-based navigation is centralized in one place.

### 6. Styling with Tailwind CSS

- **Install Tailwind CSS** for Django using the standalone CLI approach or django-tailwind package
- **Configure Tailwind** to work with Django templates
- **Use Tailwind utility classes** throughout all templates for styling:
  - Header: `bg-blue-600 text-white` with flexbox utilities (`flex justify-between items-center`)
  - Footer: `bg-blue-600 text-white text-center`
  - Body: `bg-gray-100` (light gray background)
  - Navigation: `bg-blue-600 text-white` with responsive utilities
  - Forms: Tailwind form utilities for clean, accessible styling
  - Buttons: Tailwind button utilities with hover states
  - Tables: Tailwind table utilities for user list display
- **Add Tailwind CDN** to base.html `<head>` for quick setup, or use the CLI build process for production
- Update settings.py to configure static files if using CLI build

**Why Tailwind CSS**: Utility-first approach provides rapid development, consistent design system, and responsive design out of the box. No need to write custom CSS. Tailwind's purge/JIT mode keeps production bundle sizes small.

### 7. Email Configuration (Password Recovery)

- Configure email backend in settings.py (console backend for development, SMTP for production)
- Set EMAIL_BACKEND, EMAIL_HOST, EMAIL_PORT, DEFAULT_FROM_EMAIL
- Test password reset flow

**Why email is critical**: Password recovery without email would require admin intervention for every forgotten password, creating a bottleneck.

### 8. Security Considerations

- **CSRF protection**: Ensure {% csrf_token %} in all forms
- **Password hashing**: Django handles automatically with PBKDF2
- **SQL injection**: Use ORM queries (never raw SQL with user input)
- **XSS prevention**: Django templates auto-escape by default
- **Login throttling**: Consider django-axes or implement simple throttling
- **Unique constraints**: Enforced at database level AND form validation level

**Why defense in depth**: Security must be enforced at multiple layers. Database constraints catch errors even if form validation is bypassed.

### 9. Navigation Logic

Implement context processor or template tag to determine navigation links based on user role:

```python
def navigation_context(request):
    if not request.user.is_authenticated:
        return {'nav_links': []}

    links = [
        {'url': 'workflow:dashboard', 'text': 'Workflow'},
        {'url': 'password_change', 'text': 'Cambiar Contraseña'},
    ]

    if request.user.role == 'Administrador':
        links.insert(0, {'url': 'users_admin:list', 'text': 'Administración de Usuarios'})

    return {'nav_links': links}
```

**Why context processor**: Makes navigation available in all templates without repeating logic in every view.

### 10. Testing & Verification

After implementation, verify:
- Create users with each role type
- Test login/logout flows
- Verify role-based navigation (Admin sees user admin, others don't)
- Test password change functionality
- Test password reset flow (check email in console)
- Attempt to access user admin as non-admin (should be blocked)
- Verify username and email uniqueness constraints
- Confirm users cannot be deleted, only deactivated
- Test that inactive users cannot log in

</implementation>

<constraints>

1. **Use Django built-in components**: Leverage `django.contrib.auth` for authentication, sessions, password management. Don't reinvent these wheels.

   **Why**: Django's auth system is battle-tested, secure, and handles edge cases you might miss. Custom auth systems often have security vulnerabilities.

2. **No physical deletion**: Override or remove delete functionality entirely. Only use `is_active` flag.

   **Why**: Deleted users break audit trails, foreign key relationships, and historical data. Soft deletes preserve data integrity while removing access.

3. **Database constraints**: Unique constraints on username and email at database level, not just application level.

   **Why**: Application-level checks can be bypassed (direct DB access, race conditions). Database constraints are the final line of defense.

4. **Role as CharField with choices**: Don't use separate Role table unless future requirements demand it.

   **Why**: Fixed list of 5 roles doesn't need relationship complexity. CharField with choices is simpler and performs better.

5. **Template inheritance**: Use base templates to avoid repeating header/footer/styling code.

   **Why**: DRY principle. Changes to header/footer happen in one place, not 10+ templates.

6. **Relative paths**: Reference all files relative to project root: `./workflowup/apps/users_admin/models.py`

7. **Spanish field labels**: Use Spanish text for form labels and UI text to match the user's language requirements.

</constraints>

<output>

Create the following file structure:

**Apps:**
- `./workflowup/users_admin/` - User administration app
  - `models.py` - Custom User model with role field
  - `views.py` - CRUD views for user management with role-based access control
  - `forms.py` - Forms for user creation/editing (role and is_active only for edit)
  - `urls.py` - URL patterns for user admin
  - `admin.py` - Django admin configuration (optional, for superuser access)
  - `decorators.py` - Custom decorator for admin-only access
  - `migrations/` - Database migrations

- `./workflowup/workflow/` - Main workflow app
  - `models.py` - (empty for now, future workflow models)
  - `views.py` - Dashboard view showing user info
  - `urls.py` - URL patterns for workflow
  - `migrations/` - Database migrations

**Templates:**
- `./workflowup/templates/` - Base templates directory
  - `base.html` - Master template with header, footer, styling
  - `base_authenticated.html` - Extends base, adds navigation
  - `base_anonymous.html` - Extends base, no navigation
  - `registration/login.html` - Login form
  - `registration/password_change_form.html` - Password change
  - `registration/password_change_done.html` - Success message
  - `registration/password_reset_form.html` - Request reset
  - `registration/password_reset_email.html` - Email template
  - `registration/password_reset_confirm.html` - Enter new password
  - `registration/password_reset_complete.html` - Success message
  - `users_admin/user_list.html` - List all users
  - `users_admin/user_form.html` - Create/edit user form
  - `workflow/dashboard.html` - Main workflow view

**Tailwind CSS Setup:**
- Add Tailwind CSS CDN link in `base.html` OR
- Install and configure Tailwind CLI for production builds (optional, CDN is sufficient for development)

**Configuration updates:**
- `./workflowup/workflowup/settings.py` - Update with:
  - `AUTH_USER_MODEL`
  - `TEMPLATES` dirs configuration
  - `STATIC_URL` and `STATICFILES_DIRS`
  - `LOGIN_URL` and `LOGIN_REDIRECT_URL`
  - Email backend configuration
  - Add both apps to `INSTALLED_APPS`

- `./workflowup/workflowup/urls.py` - Include:
  - Root URL pointing to login
  - Auth URLs (login, logout, password change, password reset)
  - User admin URLs (with admin-only access)
  - Workflow URLs
  - Admin site URLs (already exists)

**Context processor:**
- `./workflowup/users_admin/context_processors.py` - Navigation context based on role

</output>

<verification>

Before declaring this task complete, verify the following:

1. **Database & Models:**
   - [ ] Run `python workflowup/manage.py makemigrations` successfully
   - [ ] Run `python workflowup/manage.py migrate` successfully
   - [ ] Create test users with different roles using Django shell or admin
   - [ ] Verify username uniqueness constraint (try creating duplicate username)
   - [ ] Verify email uniqueness constraint (try creating duplicate email)

2. **Authentication Flow:**
   - [ ] Access root URL ("/") - should show login page
   - [ ] Login with valid credentials - should redirect to workflow dashboard
   - [ ] Login with invalid credentials - should show error message
   - [ ] Access workflow URL while not logged in - should redirect to login
   - [ ] Logout - should redirect to login and clear session

3. **User Administration (as Administrator):**
   - [ ] Login as user with "Administrador" role
   - [ ] Navigate to user administration (should see link in navigation)
   - [ ] View list of all users with correct fields displayed
   - [ ] Create a new user successfully
   - [ ] Edit existing user's role and is_active status
   - [ ] Verify cannot edit username, email, name fields
   - [ ] Deactivate a user
   - [ ] Verify deactivated user cannot log in
   - [ ] Confirm no delete functionality exists

4. **Authorization (as non-Administrator):**
   - [ ] Login as user with "QA" role (or any non-admin role)
   - [ ] Verify NO user administration link in navigation
   - [ ] Attempt to access user admin URLs directly - should be blocked (403 or redirect)
   - [ ] Verify CAN access workflow and password change

5. **Password Management:**
   - [ ] Access password change page from navigation
   - [ ] Successfully change password
   - [ ] Verify can log in with new password
   - [ ] Access "forgot password" link on login page
   - [ ] Submit password reset request
   - [ ] Check email (console or mailbox) for reset link
   - [ ] Click reset link and set new password
   - [ ] Verify can log in with reset password

6. **UI/UX:**
   - [ ] Verify header is blue with white text on all pages
   - [ ] Verify "WorkflowUp" appears on left of header
   - [ ] On authenticated pages, verify user name and role appear on right of header
   - [ ] Verify navigation bar appears below header (only on authenticated pages)
   - [ ] Verify navigation links match user role (admin sees user admin, others don't)
   - [ ] Verify footer is blue with white text and shows correct text
   - [ ] Verify body background is light gray
   - [ ] Verify all pages are responsive and readable

7. **Workflow App:**
   - [ ] After login, verify redirect to workflow dashboard
   - [ ] Verify dashboard shows: "Listado de Workflow de: [FirstName] [LastName] ([Role])"
   - [ ] Verify text matches the logged-in user's details

8. **Security:**
   - [ ] Verify all forms have CSRF tokens
   - [ ] Verify SQL injection attempts fail safely (try `' OR '1'='1` in login)
   - [ ] Verify XSS attempts are escaped (try `<script>alert('xss')</script>` in names)
   - [ ] Verify inactive users cannot log in
   - [ ] Verify session expires after logout

</verification>

<success_criteria>

1. ✅ Custom User model created extending AbstractUser with role field and unique constraints
2. ✅ Two Django apps created: users_admin and workflow
3. ✅ Complete authentication system: login, logout, password change, password reset
4. ✅ User administration module with create, list, update (role/active only), NO delete
5. ✅ Role-based access control: Only Administrador can access user admin
6. ✅ Role-based navigation: Different nav links based on user role
7. ✅ Workflow dashboard accessible only to authenticated users
8. ✅ All UI requirements met: blue header/footer, light gray body, correct text placement
9. ✅ Username and email uniqueness enforced at database and application levels
10. ✅ All verification steps pass successfully

</success_criteria>

<notes>

**Development workflow:**
1. Start with models and migrations (cannot undo AUTH_USER_MODEL after first migration)
2. Create superuser AFTER migrations: `python workflowup/manage.py createsuperuser`
3. Use Django admin to create test users with different roles initially
4. Build views and templates iteratively (login → workflow → user admin)
5. Test authorization thoroughly with different role types

**Common pitfalls to avoid:**
- Don't change AUTH_USER_MODEL after running first migration (would require database reset)
- Don't forget `@login_required` decorators on views
- Don't forget CSRF tokens in forms (will cause 403 errors)
- Don't use `user.delete()` anywhere (only `user.is_active = False`)
- Don't forget to configure TEMPLATES dirs in settings.py or templates won't be found

**Email backend for development:**
Use console backend to see emails in terminal:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Spanish labels reminder:**
Use Spanish throughout the UI as specified in requirements.

</notes>