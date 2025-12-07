#!/usr/bin/env python
"""
Script to set up test users with different roles.
"""
import os
import sys
import django

# Add the workflowup directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'workflowup'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workflowup.settings')
django.setup()

from users_admin.models import User

# Set password for admin superuser
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.first_name = 'Admin'
    admin.last_name = 'Sistema'
    admin.role = 'Administrador'
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_active = True
    admin.save()
    print(f"✓ Superuser 'admin' password set successfully")
    print(f"  Username: admin")
    print(f"  Password: admin123")
    print(f"  Role: {admin.role}")
except User.DoesNotExist:
    print("✗ Admin user not found")

# Create test users for each role
test_users = [
    {
        'username': 'jproyecto',
        'email': 'jproyecto@workflowup.com',
        'first_name': 'Juan',
        'last_name': 'Pérez',
        'role': 'Jefe de Proyecto',
        'password': 'test123'
    },
    {
        'username': 'scm_user',
        'email': 'scm@workflowup.com',
        'first_name': 'María',
        'last_name': 'González',
        'role': 'SCM',
        'password': 'test123'
    },
    {
        'username': 'release_mgr',
        'email': 'release@workflowup.com',
        'first_name': 'Carlos',
        'last_name': 'Rodríguez',
        'role': 'Release Manager',
        'password': 'test123'
    },
    {
        'username': 'qa_tester',
        'email': 'qa@workflowup.com',
        'first_name': 'Ana',
        'last_name': 'Martínez',
        'role': 'QA',
        'password': 'test123'
    },
]

print("\nCreating test users...")
for user_data in test_users:
    password = user_data.pop('password')
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults=user_data
    )
    if created:
        user.set_password(password)
        user.save()
        print(f"✓ Created user '{user.username}' with role '{user.role}'")
        print(f"  Username: {user.username}")
        print(f"  Password: {password}")
    else:
        print(f"✓ User '{user.username}' already exists")

print("\n" + "="*60)
print("SETUP COMPLETE!")
print("="*60)
print("\nYou can now:")
print("1. Run the development server: python workflowup/manage.py runserver")
print("2. Login with any of the test users above")
print("3. Admin user can access User Administration")
print("4. All users can access Workflow and Change Password")
print("\nTest the following scenarios:")
print("- Login as admin (can see User Administration)")
print("- Login as qa_tester (cannot see User Administration)")
print("- Create new users as admin")
print("- Edit user roles and active status")
print("- Change password")
print("- Test password reset flow")
