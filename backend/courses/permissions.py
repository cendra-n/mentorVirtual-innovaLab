from rest_framework.permissions import BasePermission

def get_user_role(user):
    """
    Función auxiliar para obtener el rol del usuario de forma segura
    desde su perfil extendido sin romper el modelo nativo de Django.
    """
    if not user or not user.is_authenticated:
        return 'STUDENT'
    if user.is_superuser or user.is_staff:
        return 'ADMIN'
    return getattr(user.profile, 'role', 'STUDENT') if hasattr(user, 'profile') else 'STUDENT'


class IsProfessorOrAdmin(BasePermission):
    """
    Permite el acceso si el usuario es Admin global del sistema 
    OR si es un Profesor verificado.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Obtenemos el rol usando el estándar seguro del perfil extendido
        user_role = get_user_role(request.user)
        return user_role in ['ADMIN', 'PROFESSOR']


class IsOwnerOrAdmin(BasePermission):
    """
    Control de Privacidad:
    - Un ADMIN puede gestionar cualquier objeto.
    - Un PROFESSOR solo puede gestionar SU propio curso, o los módulos y lecciones pertenecientes a su curso.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        user_role = get_user_role(request.user)
        
        # Si es Administrador, tiene pase libre inmediato
        if user_role == 'ADMIN':
            return True
            
        # Si es Profesor, verificamos la propiedad según el tipo de objeto
        if user_role == 'PROFESSOR':
            from .models import Course, Module, Lesson
            
            if isinstance(obj, Course):
                return obj.professor == request.user
            elif isinstance(obj, Module):
                return obj.course.professor == request.user
            elif isinstance(obj, Lesson):
                return obj.module.course.professor == request.user
            
        return False
    