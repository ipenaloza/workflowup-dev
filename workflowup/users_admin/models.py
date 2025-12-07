from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with role-based access control.

    Roles:
    - Administrador: Full system access including user management
    - Jefe de Proyecto: Project management capabilities
    - SCM: Software Configuration Management
    - Release Manager: Release management
    - QA: Quality Assurance
    """

    ROLE_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Jefe de Proyecto', 'Jefe de Proyecto'),
        ('SCM', 'SCM'),
        ('Release Manager', 'Release Manager'),
        ('QA', 'QA'),
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
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='Rol'
    )

    # Override email to make it unique and required
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )

    # Override first_name and last_name to make them required
    first_name = models.CharField(
        max_length=150,
        verbose_name='Nombre'
    )

    last_name = models.CharField(
        max_length=150,
        verbose_name='Apellido'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']

    def save(self, *args, **kwargs):
        """
        Override save to force lowercase username.
        """
        if self.username:
            self.username = self.username.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.get_full_name()} ({self.role})"

    def delete(self, *args, **kwargs):
        """
        Prevent physical deletion of users.
        Users should only be deactivated using is_active field.
        """
        raise Exception(
            "No se permite eliminar usuarios. "
            "Use is_active=False para desactivar."
        )
