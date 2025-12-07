"""
Forms for user administration.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
import re


class UserCreateForm(UserCreationForm):
    """
    Form for creating new users.
    Includes all required fields plus password fields.
    """

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'is_active']
        labels = {
            'username': 'Username',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Email',
            'role': 'Rol',
            'is_active': 'Activo',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'role': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['role'].required = True

        # Update password labels to Spanish and add Tailwind classes
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'
        self.fields['password1'].widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'})
        self.fields['password2'].widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'})

    def clean_username(self):
        """Validate username contains only letters and convert to lowercase."""
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

    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating existing users.
    Only allows editing role and is_active status.
    """

    class Meta:
        model = User
        fields = ['role', 'is_active']
        labels = {
            'role': 'Rol',
            'is_active': 'Activo',
        }
        widgets = {
            'role': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].required = True
