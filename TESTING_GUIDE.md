# WorkflowUp - Testing Guide

## Overview
This guide provides comprehensive testing steps for the WorkflowUp Django RBAC system.

## Starting the Server

```bash
cd /Users/ipenaloza/WorkflowUp/@_version_2/workflowup2/workflowup
python manage.py runserver
```

Access the application at: http://127.0.0.1:8000/

## Test Users

The following test users have been created with different roles:

### Administrator User
- **Username:** admin
- **Password:** admin123
- **Role:** Administrador
- **Access:** Full system access including user administration

### Project Manager
- **Username:** jproyecto
- **Password:** test123
- **Role:** Jefe de Proyecto
- **Access:** Workflow and password change only

### SCM User
- **Username:** scm_user
- **Password:** test123
- **Role:** SCM
- **Access:** Workflow and password change only

### Release Manager
- **Username:** release_mgr
- **Password:** test123
- **Role:** Release Manager
- **Access:** Workflow and password change only

### QA Tester
- **Username:** qa_tester
- **Password:** test123
- **Role:** QA
- **Access:** Workflow and password change only

---

## Testing Checklist

### 1. Database & Models ✓

- [x] Run `python manage.py makemigrations` successfully
- [x] Run `python manage.py migrate` successfully
- [x] Create test users with different roles
- [ ] Verify username uniqueness constraint (try creating duplicate username)
- [ ] Verify email uniqueness constraint (try creating duplicate email)

### 2. Authentication Flow

#### Login Test
- [ ] Access root URL ("/") - should display login page
- [ ] Login with valid credentials (admin/admin123) - should redirect to workflow dashboard
- [ ] Login with invalid credentials - should show error message
- [ ] Check that header shows "WorkflowUp" on left side
- [ ] Check that header shows user name and role on right side (after login)

#### Logout Test
- [ ] Click logout (if available) or access /logout/
- [ ] Verify redirect to login page
- [ ] Verify session is cleared

#### Access Control
- [ ] Try accessing workflow URL while not logged in - should redirect to login
- [ ] After login, access workflow dashboard - should work
- [ ] Try accessing /usuarios/ as non-admin - should show permission denied
- [ ] Try accessing /usuarios/ as admin - should show user list

### 3. User Administration (as Administrator)

#### Access & Navigation
- [ ] Login as admin (admin/admin123)
- [ ] Verify navigation shows: "Administración de Usuarios", "Workflow", "Cambiar Contraseña"
- [ ] Click "Administración de Usuarios" - should show user list

#### User List View
- [ ] Verify table shows columns: Usuario, Nombre, Apellido, Email, Rol, Estado, Acciones
- [ ] Verify all 5 test users are displayed
- [ ] Test search functionality (search by username, name, email)
- [ ] Test role filter dropdown
- [ ] Test active status filter
- [ ] Verify pagination (if more than 20 users)

#### Create User
- [ ] Click "Crear Usuario" button
- [ ] Fill in all required fields:
  - Usuario: testuser1
  - Nombre: Test
  - Apellido: User
  - Email: testuser1@test.com
  - Contraseña: Test123456
  - Confirmar Contraseña: Test123456
  - Rol: QA
  - Activo: Checked
- [ ] Click "Crear Usuario"
- [ ] Verify success message appears
- [ ] Verify user appears in user list
- [ ] Try creating user with duplicate username - should show error
- [ ] Try creating user with duplicate email - should show error

#### Update User
- [ ] Click "Editar" on a user
- [ ] Verify read-only fields are displayed (username, email, nombre, apellido)
- [ ] Verify only "Rol" and "Activo" fields are editable
- [ ] Change role to different value
- [ ] Click "Guardar Cambios"
- [ ] Verify success message
- [ ] Verify changes reflected in user list

#### Deactivate User
- [ ] Edit a user and uncheck "Activo"
- [ ] Save changes
- [ ] Logout and try to login as deactivated user - should fail
- [ ] Login back as admin
- [ ] Reactivate the user
- [ ] Verify user can now login

#### Delete Prevention
- [ ] Verify no delete button exists in user list
- [ ] Verify no delete functionality available anywhere

### 4. Authorization (as non-Administrator)

#### Project Manager Access
- [ ] Login as jproyecto (jproyecto/test123)
- [ ] Verify navigation shows only: "Workflow", "Cambiar Contraseña"
- [ ] Verify NO "Administración de Usuarios" link
- [ ] Try accessing /usuarios/ directly in browser - should show permission denied or redirect

#### Other Roles Access
- [ ] Repeat above tests for scm_user, release_mgr, qa_tester
- [ ] All should have same restricted access (no user administration)

### 5. Password Management

#### Password Change (Authenticated Users)
- [ ] Login as any user
- [ ] Click "Cambiar Contraseña" in navigation
- [ ] Enter current password
- [ ] Enter new password (twice)
- [ ] Click "Cambiar Contraseña"
- [ ] Verify success message
- [ ] Logout and login with new password - should work
- [ ] Logout and try old password - should fail

#### Password Reset Flow
- [ ] Logout to reach login page
- [ ] Click "¿Olvidó su contraseña?"
- [ ] Enter email address of existing user (e.g., admin@workflowup.com)
- [ ] Click "Enviar Instrucciones"
- [ ] Check terminal/console for password reset email
- [ ] Copy the reset link from console output
- [ ] Open reset link in browser
- [ ] Enter new password (twice)
- [ ] Click "Cambiar Contraseña"
- [ ] Verify success message
- [ ] Login with new password - should work

### 6. Workflow App

#### Dashboard Access
- [ ] After login, verify redirect to workflow dashboard
- [ ] Verify page shows: "Listado de Workflow de: [FirstName] [LastName] ([Role])"
- [ ] Verify user's actual name and role are displayed
- [ ] Verify placeholder content appears (projects, documents, history cards)

#### Navigation
- [ ] Click "Workflow" in navigation - should go to dashboard
- [ ] Verify all navigation links work properly

### 7. UI/UX Requirements

#### Header (All Pages)
- [ ] Login page: Blue background, white text, "WorkflowUp" on left
- [ ] After login: Blue background, white text
  - Left side: "WorkflowUp"
  - Right side: "[FirstName] [LastName] ([Role])"

#### Navigation Bar (Authenticated Pages Only)
- [ ] Verify navigation appears below header (blue background)
- [ ] Administrator: Shows "Administración de Usuarios", "Workflow", "Cambiar Contraseña"
- [ ] Other roles: Shows "Workflow", "Cambiar Contraseña"
- [ ] Hover effects work on navigation links

#### Footer (All Pages)
- [ ] Blue background, white text, centered
- [ ] Text: "2025 - Proyecto de titulo de Iván Peñaloza (i.pealozazamora@uandresbello.edu)"
- [ ] Footer sticks to bottom of page

#### Body Styling
- [ ] Light gray background on all pages
- [ ] Content properly centered and padded
- [ ] Forms are styled consistently
- [ ] Buttons have hover effects
- [ ] Tables are properly formatted
- [ ] Responsive design works on different screen sizes

### 8. Security Testing

#### CSRF Protection
- [ ] Verify all forms have {% csrf_token %}
- [ ] Try submitting form without CSRF token - should fail

#### SQL Injection
- [ ] Try SQL injection in login: username = `admin' OR '1'='1`
- [ ] Should fail safely

#### XSS Prevention
- [ ] Create user with name: `<script>alert('XSS')</script>`
- [ ] Verify script is escaped and not executed

#### Session Management
- [ ] Login successfully
- [ ] Verify session cookie is created
- [ ] Logout
- [ ] Verify session is destroyed
- [ ] Try accessing authenticated pages - should redirect to login

### 9. Edge Cases

#### Empty States
- [ ] Apply filters that return no results
- [ ] Verify "No se encontraron usuarios" message appears

#### Form Validation
- [ ] Try submitting empty required fields - should show errors
- [ ] Try mismatched passwords - should show error
- [ ] Try invalid email format - should show error

#### URL Manipulation
- [ ] Try accessing /usuarios/999/editar/ (non-existent user)
- [ ] Should show 404 or appropriate error

---

## Common Issues & Solutions

### Issue: Database migration errors
**Solution:** Reset database with `python reset_db.py` then run migrations again

### Issue: Templates not found
**Solution:** Verify TEMPLATES 'DIRS' in settings.py includes BASE_DIR / 'templates'

### Issue: Static files not loading
**Solution:** Tailwind CSS is loaded via CDN, no static file configuration needed

### Issue: Navigation links not showing
**Solution:** Verify context processor is registered in settings.py

### Issue: Permission denied on user admin
**Solution:** Verify user has 'Administrador' role, not just is_staff=True

---

## Success Criteria

All of the following must be verified:

1. ✓ Custom User model created extending AbstractUser with role field
2. ✓ Two Django apps created: users_admin and workflow
3. ✓ Complete authentication system: login, logout, password change, password reset
4. ✓ User administration module with create, list, update (role/active only), NO delete
5. ✓ Role-based access control: Only Administrador can access user admin
6. ✓ Role-based navigation: Different nav links based on user role
7. ✓ Workflow dashboard accessible only to authenticated users
8. ✓ All UI requirements met: blue header/footer, light gray body, correct text placement
9. ✓ Username and email uniqueness enforced at database and application levels
10. [ ] All verification steps tested and passing

---

## Next Steps After Testing

Once all tests pass:

1. Document any bugs found and their fixes
2. Consider adding:
   - User profile editing (for users to update their own names)
   - Admin dashboard with statistics
   - Audit logging for user changes
   - Email verification on signup
   - Two-factor authentication
   - Password strength requirements
   - Account lockout after failed attempts

3. Production preparation:
   - Change SECRET_KEY
   - Set DEBUG = False
   - Configure ALLOWED_HOSTS
   - Set up SMTP for email (not console backend)
   - Use environment variables for sensitive settings
   - Set up proper static file serving
   - Configure database backups
   - Set up monitoring and logging
