#!/usr/bin/env python
"""
Test script to verify SCM implementation.
This script tests the SCM functionality by simulating the workflow process.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'workflowup'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workflowup.settings')
django.setup()

from users_admin.models import User
from workflow.models import Workflow, Actividad
from workflow.forms import LineaBaseUpdateForm
from django.db.models import Max

def test_scm_implementation():
    """Test the SCM implementation."""
    print("=" * 80)
    print("SCM IMPLEMENTATION TEST")
    print("=" * 80)

    # Test 1: Check if SCM user exists
    print("\n1. Checking SCM user...")
    try:
        scm_user = User.objects.get(username='scm_user', role='SCM', is_active=True)
        print(f"   ✓ SCM user found: {scm_user.username} ({scm_user.first_name} {scm_user.last_name})")
    except User.DoesNotExist:
        print("   ✗ SCM user not found!")
        return False

    # Test 2: Check if Jefe de Proyecto user exists
    print("\n2. Checking Jefe de Proyecto user...")
    try:
        jp_user = User.objects.filter(role='Jefe de Proyecto', is_active=True).first()
        if jp_user:
            print(f"   ✓ Jefe de Proyecto found: {jp_user.username} ({jp_user.first_name} {jp_user.last_name})")
        else:
            print("   ✗ No Jefe de Proyecto users found!")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

    # Test 3: Check LineaBaseUpdateForm
    print("\n3. Testing LineaBaseUpdateForm...")
    try:
        form = LineaBaseUpdateForm()
        if 'linea_base' in form.fields:
            print("   ✓ LineaBaseUpdateForm has linea_base field")
        else:
            print("   ✗ LineaBaseUpdateForm missing linea_base field!")
            return False
    except Exception as e:
        print(f"   ✗ Error creating form: {e}")
        return False

    # Test 4: Check helper methods
    print("\n4. Testing Workflow helper methods...")
    try:
        workflows = Workflow.objects.all()
        if workflows.exists():
            test_workflow = workflows.first()

            # Test helper methods exist
            methods_to_test = [
                'get_actividad_workflow',
                'get_actividad_scm1',
                'get_actividad_scm2',
                'get_actividad_rm',
                'get_actividad_qa'
            ]

            for method_name in methods_to_test:
                if hasattr(test_workflow, method_name):
                    print(f"   ✓ Method {method_name} exists")
                else:
                    print(f"   ✗ Method {method_name} missing!")
                    return False
        else:
            print("   ⚠ No workflows found to test (this is okay for a fresh install)")
    except Exception as e:
        print(f"   ✗ Error testing helper methods: {e}")
        return False

    # Test 5: Check URL patterns
    print("\n5. Checking URL patterns...")
    try:
        from django.urls import reverse

        # Test workflow_detail_scm URL
        if workflows.exists():
            test_id = workflows.first().id_workflow
            url = reverse('workflow:workflow_detail_scm', kwargs={'id_workflow': test_id})
            print(f"   ✓ workflow_detail_scm URL: {url}")
        else:
            print("   ⚠ Cannot test workflow_detail_scm URL (no workflows exist)")

        # Test dashboard URL
        url = reverse('workflow:dashboard')
        print(f"   ✓ dashboard URL: {url}")

    except Exception as e:
        print(f"   ✗ Error testing URLs: {e}")
        return False

    # Test 6: Verify dashboard logic
    print("\n6. Testing SCM dashboard logic...")
    try:
        # Simulate finding SCM workflows
        all_workflows = Workflow.objects.all().prefetch_related('actividades')
        scm_workflows = []

        for workflow in all_workflows:
            ultima_actividad = workflow.get_actividad_workflow()
            if ultima_actividad and ultima_actividad.estado_workflow == 'Activo':
                actividad_scm1 = workflow.get_actividad_scm1()
                actividad_scm2 = workflow.get_actividad_scm2()

                if actividad_scm1 and actividad_scm1.estado_proceso == 'En Proceso':
                    scm_workflows.append(workflow)
                elif actividad_scm2 and actividad_scm2.estado_proceso == 'En Proceso':
                    scm_workflows.append(workflow)

        print(f"   ✓ Found {len(scm_workflows)} workflow(s) with SCM activities in process")

    except Exception as e:
        print(f"   ✗ Error testing dashboard logic: {e}")
        return False

    # Test 7: Check template files exist
    print("\n7. Checking template files...")
    import os
    templates_dir = os.path.join(os.path.dirname(__file__), 'workflowup', 'templates', 'workflow')

    templates = [
        'dashboard_scm.html',
        'workflow_detail_scm.html'
    ]

    for template in templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            size = os.path.getsize(template_path)
            print(f"   ✓ {template} exists ({size} bytes)")
        else:
            print(f"   ✗ {template} not found!")
            return False

    # Test 8: Verify view imports
    print("\n8. Verifying view imports...")
    try:
        from workflow.views import workflow_detail_scm, dashboard
        print("   ✓ workflow_detail_scm view imported successfully")
        print("   ✓ dashboard view imported successfully")
    except ImportError as e:
        print(f"   ✗ Error importing views: {e}")
        return False

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)
    print("\nSCM Implementation Summary:")
    print("- SCM dashboard at: /workflow/")
    print("- SCM detail view at: /workflow/<id>/scm/")
    print("- LineaBaseUpdateForm created for editing línea base")
    print("- Helper methods available on Workflow model")
    print("- Both templates created successfully")
    print("\nNext steps:")
    print("1. Login as SCM user (scm_user)")
    print("2. Navigate to workflow dashboard")
    print("3. Create a workflow as Jefe de Proyecto")
    print("4. Request 'línea base' from Jefe de Proyecto")
    print("5. Login as SCM and approve/reject")
    print("=" * 80)

    return True

if __name__ == '__main__':
    try:
        success = test_scm_implementation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
