# WorkflowUp - Quick Start Guide

## Get Started in 3 Steps

### Step 1: Start the Server

```bash
cd /Users/ipenaloza/WorkflowUp/@_version_2/workflowup2/workflowup
python manage.py runserver
```

### Step 2: Open Your Browser

Navigate to: **http://127.0.0.1:8000/**

### Step 3: Login

Use any of these test accounts:

#### Administrator (Full Access)
- **Username:** admin
- **Password:** admin123
- **Can access:** User Administration + Workflow + Password Change

#### Other Roles (Workflow Only)
- **Username:** qa_tester
- **Password:** test123
- **Can access:** Workflow + Password Change

---

## What You Can Do

### As Administrator (admin/admin123)

1. **Manage Users**
   - Click "Administración de Usuarios" in navigation
   - Create new users
   - Edit user roles and active status
   - Search and filter users

2. **View Workflow**
   - Click "Workflow" in navigation
   - See your dashboard

3. **Change Password**
   - Click "Cambiar Contraseña"
   - Enter old and new passwords

### As Regular User (qa_tester/test123)

1. **View Workflow**
   - Your dashboard shows after login

2. **Change Password**
   - Click "Cambiar Contraseña"

---

## Test Password Reset

1. Logout
2. Click "¿Olvidó su contraseña?"
3. Enter email: admin@workflowup.com
4. Check your terminal for reset link
5. Copy and paste link in browser
6. Set new password

---

## Available Test Users

| Username | Password | Role | Email |
|----------|----------|------|-------|
| admin | admin123 | Administrador | admin@workflowup.com |
| jproyecto | test123 | Jefe de Proyecto | jproyecto@workflowup.com |
| scm_user | test123 | SCM | scm@workflowup.com |
| release_mgr | test123 | Release Manager | release@workflowup.com |
| qa_tester | test123 | QA | qa@workflowup.com |

---

## Quick Tests

### Test 1: Role-Based Access
1. Login as **qa_tester** (test123)
2. Notice: Only "Workflow" and "Cambiar Contraseña" in navigation
3. Try accessing: http://127.0.0.1:8000/usuarios/
4. Should see: Permission denied

### Test 2: Create New User
1. Login as **admin** (admin123)
2. Click "Administración de Usuarios"
3. Click "Crear Usuario"
4. Fill form and submit
5. See new user in list

### Test 3: Edit User Role
1. Login as **admin** (admin123)
2. Click "Administración de Usuarios"
3. Click "Editar" on any user
4. Change role
5. Save changes

---

## Need More Info?

- **Full Documentation:** See IMPLEMENTATION_SUMMARY.md
- **Testing Guide:** See TESTING_GUIDE.md
- **Project Structure:** See CLAUDE.md

---

## Troubleshooting

### Server won't start
```bash
# Check for port conflicts
lsof -i :8000

# Try different port
python manage.py runserver 8080
```

### Database errors
```bash
# Reset database
python reset_db.py
python manage.py migrate
python setup_users.py
```

### Can't login
- Check username spelling (case-sensitive)
- Verify password is correct
- Check user is_active flag

---

## Stop the Server

Press `Ctrl+C` in terminal

---

## What's Next?

Once you've explored the system:

1. Review TESTING_GUIDE.md for comprehensive testing
2. Read IMPLEMENTATION_SUMMARY.md for architecture details
3. Customize for your project requirements
4. Add workflow-specific features

---

**Enjoy using WorkflowUp!**
