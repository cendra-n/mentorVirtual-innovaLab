from rest_framework.permissions import BasePermission
from rest_framework import exceptions

def get_user_role(user):
    """
     Me logie desde swagger como alumno y me puso como student y is_staff_true.
       Como no se donde origina ese cambio, 
       cambie los permisos aca solamente para "ENROLLMENT"
    """
    if not user or not user.is_authenticated:
        return 'STUDENT'
    
    # Quitamos is_staff de aquí si no quieres que cualquier staff sea admin
    if user.is_superuser:
        return 'ADMIN'
        
    return getattr(user.profile, 'role', 'STUDENT') if hasattr(user, 'profile') else 'STUDENT'

#Puse estos permisos para que en la lista de inscripciones solo pudiera acceder admin y profesor
class IsOwnerOrAdmin(BasePermission):
    """
    Control de Privacidad:
    - Un ADMIN puede gestionar cualquier objeto.
    - Un PROFESSOR solo puede ver inscripciones de sus cursos
    """
    # Este método se ejecuta antes de entrar a la vista
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        role = get_user_role(request.user)
        # Verificamos si es ADMIN o PROFESSOR
        if role in ['ADMIN', 'PROFESSOR']:
            return True
        
        # Si llega aquí es porque es STUDENT, lanzamos el error con el mensaje
        raise exceptions.PermissionDenied("Si no es Admin o profesor, no puede visualizar este contenido.")
       
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