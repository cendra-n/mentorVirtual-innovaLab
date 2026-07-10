from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, UserConfig, ProfessorProfile

# 1. Formulario incrustado para la Configuración de Accesibilidad
class UserConfigInline(admin.StackedInline):
    model = UserConfig
    can_delete = False
    verbose_name_plural = "Preferencias de Accesibilidad (UserConfig)"

# 2. Formulario incrustado para los datos comunes y de Roles
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Datos de Perfil General (Roles)"

# 3. Formulario incrustado para los datos contractuales del Profesor
class ProfessorProfileInline(admin.StackedInline):
    model = ProfessorProfile
    can_delete = True  # Si deja de ser profesor, permite remover su legajo del Ministerio
    verbose_name_plural = "Datos Contractuales del Profesor (Requerimiento Ministerio)"

# 4. Extendemos el administrador de usuarios nativo de Django
class UserAdmin(BaseUserAdmin):
    # Metemos los tres formularios en orden jerárquico dentro de la misma vista
    inlines = [UserProfileInline, UserConfigInline, ProfessorProfileInline]
    list_display = ('username', 'email', 'get_role', 'is_staff')
    list_filter = ('profile__role', 'is_staff')

    # Método para renderizar de manera limpia el Rol en la tabla principal
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else "Sin Perfil"
    get_role.short_description = 'Rol Asignado'

# 5. Desregistramos el comportamiento por defecto y aplicamos el nuevo diseño unificado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)