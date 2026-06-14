from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """Permite el acceso únicamente a usuarios administradores."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'

class IsProfessorUser(BasePermission):
    """Permite el acceso únicamente a profesores."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'PROFESSOR'

class IsStudentUser(BasePermission):
    """Permite el acceso únicamente a alumnos."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'STUDENT'