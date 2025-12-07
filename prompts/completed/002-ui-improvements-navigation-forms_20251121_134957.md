<objective>
Implement UI/UX improvements to the Django RBAC system focusing on:
1. Add logout option to navigation bar
2. Right-align navigation links
3. Highlight active page in navigation with underline
4. Fix form field alignment issues (buttons, textboxes, listboxes)
5. Username validation: only letters, forced lowercase

These improvements will enhance user experience and fix visual inconsistencies in the interface.
</objective>

<context>
This is an existing Django 5.2.8 project with two apps (users_admin and workflow) using Tailwind CSS for styling. The navigation bar is rendered via context processor and currently shows role-based links but lacks logout option and visual feedback for the current page.

Review the following files:
- @workflowup/users_admin/context_processors.py - Navigation context
- @workflowup/templates/base_authenticated.html - Navigation rendering
- @workflowup/users_admin/forms.py - Form definitions
- @workflowup/users_admin/models.py - User model with username field
- @workflowup/templates/users_admin/user_form.html - Form template
- @workflowup/templates/users_admin/user_list.html - List template
</context>

<requirements>

## 1. Add Logout to Navigation Bar

- Add "Cerrar Sesión" (Logout) as the LAST option in the navigation bar
- Should appear for ALL authenticated users (all roles)
- Link to Django's logout view
- Position: Last item on the right side of navigation

## 2. Right-Align Navigation Links

- Move all navigation links to the RIGHT side of the navigation bar
- Left side of navigation bar should be empty
- Maintain proper spacing between links
- Use Tailwind flexbox utilities (flex, justify-end, space-x-4, etc.)

## 3. Active Page Highlighting

- Detect which page the user is currently viewing
- Apply underline styling to the active navigation link
- Use Tailwind utility: `underline` or `border-b-2 border-white`
- Active state should be clearly visible
- Implement using Django's `{% url %}` tag comparison or request.path checking

## 4. Fix Form Field Alignment

**Problem**: When multiple form elements (textboxes, select boxes, buttons) appear in the same row, they are misaligned vertically.

**Solution**:
- Apply consistent Tailwind classes for vertical alignment
- Use flexbox with `items-center` or `items-end` for proper alignment
- Ensure all input fields have same height classes
- Add proper spacing between elements
- Fix issues in:
  - User list search/filter form
  - User create form
  - User edit form
  - Any inline form elements

**Specific fixes needed**:
- Search textbox + filter select + search button alignment
- Form labels and inputs vertical spacing
- Submit/cancel button alignment
- Table action buttons alignment

## 5. Username Validation

**Requirements**:
- Username field must accept ONLY letters (a-z, A-Z)
- No numbers, spaces, special characters allowed
- Automatically convert input to lowercase before saving
- Add validation at model level and form level
- Show clear error message: "El username solo puede contener letras (a-z)"
- Apply lowercase transformation in form's clean_username method

</requirements>

<implementation>

## Step 1: Update Context Processor (users_admin/context_processors.py)

Add logout link as last item in nav_links:

```python
def navigation_context(request):
    if not request.user.is_authenticated:
        return {'nav_links': []}

    links = []

    if request.user.role == 'Administrador':
        links.append({'url': 'users_admin:user_list', 'text': 'Administración de Usuarios', 'name': 'user_list'})

    links.append({'url': 'workflow:dashboard', 'text': 'Workflow', 'name': 'dashboard'})
    links.append({'url': 'password_change', 'text': 'Cambiar Contraseña', 'name': 'password_change'})
    links.append({'url': 'logout', 'text': 'Cerrar Sesión', 'name': 'logout'})

    return {'nav_links': links}
```

**Key changes**:
- Added 'name' field to each link for active state detection
- Added logout as last item
- Used URL names that match urls.py configuration

## Step 2: Update Navigation Template (templates/base_authenticated.html)

Update the navigation bar rendering:

```html
<!-- Navigation Bar -->
<nav class="bg-blue-600">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-end items-center h-12 space-x-6">
            {% for link in nav_links %}
                {% url link.url as link_url %}
                <a href="{{ link_url }}"
                   class="text-white hover:text-gray-200 transition
                          {% if request.resolver_match.url_name == link.name or request.path == link_url %}
                              underline font-semibold
                          {% endif %}">
                    {{ link.text }}
                </a>
            {% endfor %}
        </div>
    </div>
</nav>
```

**Key changes**:
- `justify-end` - Aligns links to the right
- `space-x-6` - Consistent spacing between links
- Active state detection using `request.resolver_match.url_name` or `request.path`
- `underline font-semibold` - Highlights active link

## Step 3: Update User Model (users_admin/models.py)

Add username validation:

```python
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model with role-based access control"""

    # Role choices
    ADMINISTRADOR = 'Administrador'
    JEFE_PROYECTO = 'Jefe de Proyecto'
    SCM = 'SCM'
    RELEASE_MANAGER = 'Release Manager'
    QA = 'QA'

    ROLE_CHOICES = [
        (ADMINISTRADOR, 'Administrador'),
        (JEFE_PROYECTO, 'Jefe de Proyecto'),
        (SCM, 'SCM'),
        (RELEASE_MANAGER, 'Release Manager'),
        (QA, 'QA'),
    ]

    # Username validator: only letters
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z]+$',
        message='El username solo puede contener letras (a-z)',
        code='invalid_username'
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        help_text='Requerido. 150 caracteres o menos. Solo letras.',
        error_messages={
            'unique': 'Ya existe un usuario con este username.',
        },
    )

    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=QA,
        verbose_name='Rol'
    )

    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        error_messages={
            'unique': 'Ya existe un usuario con este email.',
        }
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def save(self, *args, **kwargs):
        # Force lowercase username
        if self.username:
            self.username = self.username.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
```

**Key changes**:
- Added `username_validator` with regex `^[a-zA-Z]+$`
- Override `save()` method to force lowercase
- Custom error messages in Spanish

## Step 4: Update Forms (users_admin/forms.py)

Add username validation and lowercase conversion:

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
import re

class UserCreateForm(UserCreationForm):
    """Form for creating new users"""

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2']
        labels = {
            'username': 'Username',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Email',
            'role': 'Rol',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'first_name': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'last_name': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'role': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'})
        self.fields['password2'].widget.attrs.update({'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'})
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'

    def clean_username(self):
        username = self.cleaned_data.get('username', '')

        # Check if only letters
        if not re.match(r'^[a-zA-Z]+$', username):
            raise forms.ValidationError('El username solo puede contener letras (a-z)')

        # Convert to lowercase
        username = username.lower()

        # Check uniqueness
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ya existe un usuario con este username.')

        return username


class UserUpdateForm(forms.ModelForm):
    """Form for updating existing users (role and is_active only)"""

    class Meta:
        model = User
        fields = ['role', 'is_active']
        labels = {
            'role': 'Rol',
            'is_active': 'Usuario Activo',
        }
        widgets = {
            'role': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'}),
        }
```

**Key changes**:
- `clean_username()` method validates letters-only and converts to lowercase
- Clear Spanish error messages
- Consistent Tailwind classes for all form fields

## Step 5: Fix Form Field Alignment (templates/users_admin/user_list.html)

Update search/filter form:

```html
<!-- Search and Filter Section -->
<div class="mb-6 bg-white p-4 rounded-lg shadow">
    <form method="get" class="flex flex-wrap items-end gap-4">
        <!-- Search Input -->
        <div class="flex-1 min-w-[200px]">
            <label for="search" class="block text-sm font-medium text-gray-700 mb-1">
                Buscar
            </label>
            <input type="text"
                   id="search"
                   name="search"
                   value="{{ request.GET.search }}"
                   placeholder="Username, nombre, apellido o email"
                   class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">
        </div>

        <!-- Role Filter -->
        <div class="w-48">
            <label for="role" class="block text-sm font-medium text-gray-700 mb-1">
                Filtrar por Rol
            </label>
            <select name="role"
                    id="role"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="">Todos los roles</option>
                {% for role_value, role_label in roles %}
                    <option value="{{ role_value }}" {% if request.GET.role == role_value %}selected{% endif %}>
                        {{ role_label }}
                    </option>
                {% endfor %}
            </select>
        </div>

        <!-- Status Filter -->
        <div class="w-40">
            <label for="status" class="block text-sm font-medium text-gray-700 mb-1">
                Estado
            </label>
            <select name="status"
                    id="status"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="">Todos</option>
                <option value="active" {% if request.GET.status == 'active' %}selected{% endif %}>Activos</option>
                <option value="inactive" {% if request.GET.status == 'inactive' %}selected{% endif %}>Inactivos</option>
            </select>
        </div>

        <!-- Buttons -->
        <div class="flex gap-2">
            <button type="submit"
                    class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition">
                Buscar
            </button>
            <a href="{% url 'users_admin:user_list' %}"
               class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition">
                Limpiar
            </a>
        </div>
    </form>
</div>
```

**Key changes**:
- `flex flex-wrap items-end gap-4` - Aligns all elements to bottom with consistent gaps
- All inputs have same height: `py-2`
- Labels have `mb-1` for consistent spacing
- Buttons wrapped in div with `flex gap-2`

## Step 6: Fix Form Field Alignment (templates/users_admin/user_form.html)

Update form layout:

```html
{% extends 'base_authenticated.html' %}

{% block title %}
    {% if form.instance.pk %}Editar Usuario{% else %}Crear Usuario{% endif %} - WorkflowUp
{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto">
    <div class="bg-white shadow-md rounded-lg overflow-hidden">
        <!-- Header -->
        <div class="bg-blue-600 text-white px-6 py-4">
            <h2 class="text-2xl font-bold">
                {% if form.instance.pk %}
                    Editar Usuario: {{ form.instance.username }}
                {% else %}
                    Crear Nuevo Usuario
                {% endif %}
            </h2>
        </div>

        <!-- Form -->
        <form method="post" class="px-6 py-6">
            {% csrf_token %}

            <!-- Error Messages -->
            {% if form.non_field_errors %}
                <div class="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    {{ form.non_field_errors }}
                </div>
            {% endif %}

            <!-- Form Fields -->
            <div class="space-y-4">
                {% for field in form %}
                    <div>
                        <label for="{{ field.id_for_label }}" class="block text-sm font-medium text-gray-700 mb-1">
                            {{ field.label }}
                            {% if field.field.required %}
                                <span class="text-red-500">*</span>
                            {% endif %}
                        </label>

                        {{ field }}

                        {% if field.help_text %}
                            <p class="mt-1 text-sm text-gray-500">{{ field.help_text }}</p>
                        {% endif %}

                        {% if field.errors %}
                            <p class="mt-1 text-sm text-red-600">{{ field.errors.0 }}</p>
                        {% endif %}
                    </div>
                {% endfor %}
            </div>

            <!-- Buttons -->
            <div class="mt-6 flex items-center gap-3">
                <button type="submit"
                        class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition">
                    {% if form.instance.pk %}Actualizar{% else %}Crear{% endif %}
                </button>
                <a href="{% url 'users_admin:user_list' %}"
                   class="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition">
                    Cancelar
                </a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
```

**Key changes**:
- `space-y-4` - Consistent vertical spacing between fields
- `items-center` on button container for alignment
- All buttons have same padding: `px-6 py-2`
- `gap-3` for button spacing

## Step 7: Create Migration for Username Changes

Since we're modifying the username field validator, create a migration:

```bash
python workflowup/manage.py makemigrations users_admin
python workflowup/manage.py migrate
```

</implementation>

<verification>

After implementation, verify:

1. **Navigation Bar:**
   - [ ] "Cerrar Sesión" appears as last item
   - [ ] All navigation links are right-aligned
   - [ ] Active page link is underlined
   - [ ] Navigation works for all roles (Admin sees 4 links, others see 3)
   - [ ] Logout functionality works

2. **Username Validation:**
   - [ ] Try creating user with numbers: "user123" → Should fail
   - [ ] Try creating user with spaces: "user name" → Should fail
   - [ ] Try creating user with special chars: "user@test" → Should fail
   - [ ] Try creating user with uppercase: "UserTest" → Should save as "usertest"
   - [ ] Try creating user with only letters: "username" → Should work
   - [ ] Error message in Spanish appears for invalid usernames

3. **Form Field Alignment:**
   - [ ] User list search form: textbox, selects, and buttons align properly
   - [ ] User create form: all fields have consistent spacing
   - [ ] User edit form: fields and buttons align correctly
   - [ ] All forms look good on different screen sizes

4. **Visual Consistency:**
   - [ ] All buttons have same height
   - [ ] All input fields have same height
   - [ ] Labels have consistent spacing above fields
   - [ ] Gaps between elements are consistent

</verification>

<success_criteria>

1. ✅ Logout link added to navigation (last position, right-aligned)
2. ✅ Navigation links moved to right side of navbar
3. ✅ Active page highlighted with underline
4. ✅ Form elements properly aligned (search forms, create/edit forms)
5. ✅ Username accepts only letters
6. ✅ Username automatically converted to lowercase
7. ✅ Clear Spanish error messages for invalid usernames
8. ✅ All UI elements have consistent Tailwind styling
9. ✅ Responsive design maintained across all changes

</success_criteria>

<notes>

**Username validation approach:**
- Model-level: RegexValidator in User model
- Form-level: clean_username() method
- Database: Stored in lowercase via save() override
- Double validation ensures data integrity

**Active link detection:**
- Uses `request.resolver_match.url_name` to match against link 'name' field
- Fallback to `request.path` comparison
- Both methods ensure accurate highlighting

**Tailwind alignment classes:**
- `items-end` - Aligns flex items to bottom (for form elements with labels)
- `items-center` - Centers items vertically (for buttons)
- `space-x-*` / `gap-*` - Consistent spacing
- `py-2` - Standard height for inputs and buttons

</notes>