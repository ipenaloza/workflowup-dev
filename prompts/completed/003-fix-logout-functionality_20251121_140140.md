<objective>
Fix the logout functionality that is currently not working. The logout URL is giving an error and not properly logging out users. Implement proper logout view using Django's built-in authentication views and ensure it redirects correctly to the login page after logout.
</objective>

<context>
The Django RBAC system has a navigation link to "Cerrar Sesión" (logout) but the URL is not properly configured or the view is missing. Users are getting an error when clicking the logout link.

Review the following files:
- @workflowup/workflowup/urls.py - Main URL configuration
- @workflowup/users_admin/context_processors.py - Navigation context with logout link
- @workflowup/workflowup/settings.py - Check LOGOUT_REDIRECT_URL setting

Django provides built-in logout functionality through `django.contrib.auth.views.LogoutView` which should be used.
</context>

<requirements>

## Logout Functionality Requirements

1. **Use Django's built-in LogoutView**
   - Import and configure `django.contrib.auth.views.LogoutView`
   - This is the recommended Django approach for handling logout

2. **URL Configuration**
   - Configure logout URL pattern in `workflowup/urls.py`
   - URL name should be 'logout' to match the navigation link
   - URL path should be '/logout/' or similar

3. **Redirect After Logout**
   - After successful logout, redirect user to login page
   - Configure `LOGOUT_REDIRECT_URL` in settings.py
   - Should point to 'login' or '/' (which is the login page)

4. **Session Cleanup**
   - Ensure Django properly clears the session
   - Django's LogoutView handles this automatically

5. **No Template Required**
   - LogoutView doesn't need a template when using next_page parameter
   - It will redirect immediately after logout

</requirements>

<implementation>

## Step 1: Configure Logout URL (workflowup/urls.py)

Add the logout URL pattern using Django's built-in LogoutView:

```python
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # App URLs
    path('usuarios/', include('users_admin.urls')),
    path('workflow/', include('workflow.urls')),
]
```

**Key changes**:
- Added `from django.contrib.auth import views as auth_views`
- Added `path('logout/', auth_views.LogoutView.as_view(), name='logout')`
- Uses Django's built-in LogoutView which handles session cleanup automatically

## Step 2: Configure Logout Redirect in Settings (workflowup/settings.py)

Add or update the LOGOUT_REDIRECT_URL setting:

```python
# Authentication settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'workflow:dashboard'
LOGOUT_REDIRECT_URL = 'login'  # Redirect to login page after logout
```

**Why this works**:
- `LOGOUT_REDIRECT_URL = 'login'` tells Django where to redirect after logout
- Since '/' is the login page, users will see the login form after logout
- Django's LogoutView reads this setting automatically

## Step 3: Verify Navigation Link (users_admin/context_processors.py)

Ensure the logout link in navigation uses the correct URL name:

```python
def navigation_context(request):
    """Provide navigation links based on user role"""
    if not request.user.is_authenticated:
        return {'nav_links': []}

    links = []

    # Admin-only link
    if request.user.role == 'Administrador':
        links.append({
            'url': 'users_admin:user_list',
            'text': 'Administración de Usuarios',
            'name': 'user_list'
        })

    # Common links for all authenticated users
    links.append({
        'url': 'workflow:dashboard',
        'text': 'Workflow',
        'name': 'dashboard'
    })

    links.append({
        'url': 'password_change',
        'text': 'Cambiar Contraseña',
        'name': 'password_change'
    })

    # Logout link (last item)
    links.append({
        'url': 'logout',
        'text': 'Cerrar Sesión',
        'name': 'logout'
    })

    return {'nav_links': links}
```

**Verification**:
- The 'url' field is 'logout' which matches the URL name in urls.py
- This should already be correct from the previous implementation

## Alternative Approach: Custom Logout View (Optional)

If you want more control over the logout process, you can create a custom view:

**Create:** `workflowup/users_admin/views.py` (add this view)

```python
from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    """Custom logout view with explicit redirect"""
    logout(request)
    return redirect('login')
```

**Update:** `workflowup/urls.py`

```python
from users_admin.views import user_logout

urlpatterns = [
    # ... other patterns ...
    path('logout/', user_logout, name='logout'),
    # ... other patterns ...
]
```

**Note**: This approach is optional. The built-in LogoutView is preferred as it follows Django best practices.

</implementation>

<verification>

After implementation, verify the following:

1. **Logout URL Resolves:**
   - [ ] Run: `python workflowup/manage.py show_urls | grep logout` (if django-extensions installed)
   - [ ] Or manually check that '/logout/' URL is configured
   - [ ] Navigate to http://127.0.0.1:8000/logout/ - should not show error

2. **Logout Functionality:**
   - [ ] Login as any user (e.g., admin/admin123)
   - [ ] Verify you can see authenticated pages
   - [ ] Click "Cerrar Sesión" in navigation
   - [ ] Should redirect to login page
   - [ ] Verify you're logged out (try accessing /workflow/ - should redirect to login)

3. **Session Cleanup:**
   - [ ] After logout, check browser dev tools → Application → Cookies
   - [ ] Session cookie should be cleared
   - [ ] Attempting to access protected pages should redirect to login

4. **Navigation Link:**
   - [ ] "Cerrar Sesión" link should be visible in navigation
   - [ ] Link should be clickable
   - [ ] No 404 or other errors when clicked

</verification>

<success_criteria>

1. ✅ Logout URL properly configured in urls.py using LogoutView
2. ✅ LOGOUT_REDIRECT_URL set to 'login' in settings.py
3. ✅ Clicking "Cerrar Sesión" logs out the user
4. ✅ After logout, user is redirected to login page
5. ✅ Session is properly cleared (no access to protected pages)
6. ✅ No errors or 404s when accessing logout URL
7. ✅ User can log back in after logout

</success_criteria>

<notes>

**Why use Django's LogoutView?**
- Handles session cleanup automatically
- Handles CSRF token validation (for POST requests)
- Follows Django security best practices
- Configurable via settings (LOGOUT_REDIRECT_URL)
- Well-tested and maintained by Django core team

**Common Logout Issues:**
1. **Missing URL pattern** - Solution: Add LogoutView to urls.py
2. **Wrong URL name** - Solution: Ensure name='logout' in urls.py
3. **No redirect configured** - Solution: Set LOGOUT_REDIRECT_URL in settings.py
4. **CSRF token issues** - Solution: LogoutView handles this automatically

**Logout Methods in Django:**
1. **Built-in LogoutView (Recommended)** - Clean, automatic, follows best practices
2. **Custom view with logout()** - More control, but requires manual session handling
3. **Function-based view** - Simple but less feature-rich

This implementation uses method #1 (LogoutView) as it's the most robust and follows Django conventions.

</notes>