"""
Views for user administration.
Only accessible by users with 'Administrador' role.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.db.models import Q

from .models import User
from .forms import UserCreateForm, UserUpdateForm


class AdminRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the user to have 'Administrador' role.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'Administrador'

    def handle_no_permission(self):
        messages.error(self.request, 'No tiene permisos para acceder a esta página.')
        return super().handle_no_permission()


class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """
    Display a list of all users with search and filter capabilities.
    """
    model = User
    template_name = 'users_admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        # Filter by role
        role_filter = self.request.GET.get('role', '')
        if role_filter:
            queryset = queryset.filter(role=role_filter)

        # Filter by active status
        active_filter = self.request.GET.get('active', '')
        if active_filter == 'true':
            queryset = queryset.filter(is_active=True)
        elif active_filter == 'false':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['active_filter'] = self.request.GET.get('active', '')
        context['role_choices'] = User.ROLE_CHOICES
        return context


class UserCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """
    Create a new user.
    """
    model = User
    form_class = UserCreateForm
    template_name = 'users_admin/user_form.html'
    success_url = reverse_lazy('users_admin:user_list')

    def form_valid(self, form):
        messages.success(self.request, f'Usuario {form.instance.username} creado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Crear Usuario'
        context['submit_text'] = 'Crear Usuario'
        return context


class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """
    Update an existing user's role and active status.
    Only role and is_active fields can be edited.
    """
    model = User
    form_class = UserUpdateForm
    template_name = 'users_admin/user_form.html'
    success_url = reverse_lazy('users_admin:user_list')

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Usuario {form.instance.username} actualizado exitosamente.'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Editar Usuario: {self.object.username}'
        context['submit_text'] = 'Guardar Cambios'
        context['is_update'] = True
        context['user_obj'] = self.object
        return context
