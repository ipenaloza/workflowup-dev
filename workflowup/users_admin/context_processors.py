"""
Context processors for users_admin app.
Provides navigation links based on user role.
"""


def navigation_context(request):
    """
    Add navigation links to context based on user's role.

    Returns:
        dict: Context dictionary with 'nav_links' list.
              Each link has 'url' (URL name), 'text' (display text), and 'name' (for active state detection).
    """
    if not request.user.is_authenticated:
        return {'nav_links': []}

    # Base navigation links available to all authenticated users
    links = []

    # Add user administration link for Administrador role
    if request.user.role == 'Administrador':
        links.append({'url': 'users_admin:user_list', 'text': 'Administración de Usuarios', 'name': 'user_list'})

    # Workflow link for all authenticated users
    links.append({'url': 'workflow:dashboard', 'text': 'Workflow', 'name': 'dashboard'})

    # Add "Crear Workflow" link for Jefe de Proyecto
    if request.user.role == 'Jefe de Proyecto':
        links.append({'url': 'workflow:workflow_create', 'text': 'Crear Workflow', 'name': 'workflow_create'})

    # Password change link
    links.append({'url': 'password_change', 'text': 'Cambiar Contraseña', 'name': 'password_change'})

    # Logout link - always last
    links.append({'url': 'logout', 'text': 'Cerrar Sesión', 'name': 'logout'})

    return {'nav_links': links}
