"""
users/models.py

UserProfile  — datos de perfil (phone, avatar_url, bio_face_hash para biometría futura)
UserConfig   — preferencias de accesibilidad (font_size, high_contrast, voice_guidance)
StudentProfile — métricas, progreso y comportamiento para análisis de datos.

Ambos se crean automáticamente via señales al crear un User.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

# ── Analítica de eventos de usuario (Paula) ─────────────────
class EventTypes:
    LOGIN = 'login'
    LOGOUT = 'logout'
    VIDEO_PLAY = 'video_play'
    CHALLENGE_COMPLETED = 'challenge_completed'

# ── Entidades geográficas (Paula) ────────────────
class Nationality(models.Model):
    nationality_id = models.AutoField(primary_key=True)
    nationality_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.nationality_name} ({self.nationality_id})"

    class Meta:
        verbose_name = "Nacionalidad"
        verbose_name_plural = "Nacionalidades"

class Country(models.Model):
    country_id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.country_name} ({self.country_id})"

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"

class Province(models.Model):
    province_id = models.AutoField(primary_key=True)
    province_name = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='provinces')

    def __str__(self):
        return f"{self.province_name} ({self.province_id}) - {self.country.country_name}"

    class Meta:
        verbose_name = "Provincia"
        verbose_name_plural = "Provincias"

class Locality(models.Model):
    locality_id = models.AutoField(primary_key=True)
    locality_name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='localities')

    def __str__(self):
        return f"{self.locality_name} ({self.locality_id}) - {self.province.province_name}, {self.province.country.country_name}"

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"
        unique_together = ('locality_name', 'province')


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile',
        help_text="Usuario Django propietario de este perfil."
    )
    bio_face_hash = models.TextField(
        null=True, blank=True,
        help_text="Hash/embedding del rostro para autenticación biométrica (Fase 3)."
    )
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('STUDENT', 'Alumno'),
        ('PROFESSOR', 'Profesor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')

    avatar_url = models.CharField(
        max_length=255, blank=True,
        help_text="URL de la imagen de avatar del usuario."
    )
    phone = models.CharField(
        max_length=50, blank=True,
        help_text="Número telefónico de contacto."
    )

    nationality = models.ForeignKey(
        Nationality, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Nacionalidad del usuario."
    )
    country_residence = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="País de residencia del usuario."
    )
    province_residence = models.ForeignKey(
        Province, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Provincia de residencia del usuario."
    )
    locality_residence = models.ForeignKey(
        Locality, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Localidad de residencia del usuario."
    )
    internet_access = models.BooleanField(
        default=True,
        help_text="Indica si el usuario tiene acceso a internet."
    )
    SESSION_STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
    ]
    session_status = models.CharField(
        max_length=10, choices=SESSION_STATUS_CHOICES, default='OFFLINE'
    )

    def __str__(self):
        return f"Perfil de {self.user.username}"


class UserConfig(models.Model):
    FONT_SIZE_CHOICES = [
        ('SMALL',  'Small'),
        ('MEDIUM', 'Medium'),
        ('LARGE',  'Large'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='config',
        help_text="Usuario propietario de esta configuración."
    )
    font_size = models.CharField(
        max_length=10, choices=FONT_SIZE_CHOICES, default='MEDIUM',
        help_text="Tamaño de tipografía para accesibilidad."
    )
    high_contrast = models.BooleanField(
        default=False,
        help_text="Activar contraste elevado para accesibilidad."
    )
    voice_guidance = models.BooleanField(
        default=False,
        help_text="Activar guía por voz para accesibilidad."
    )

    def __str__(self):
        return f"Configuración de {self.user.username}"
    

# ── MODELOS DE DATA ANALYTICS ────────────────

class StudentProfile(models.Model):
    """
    Perfil extendido exclusivo para los estudiantes.
    Diseñado para capturar métricas de engagement, progreso y calidad de datos
    para su posterior explotación analítica.
    """
    
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='student_analytics',
        help_text='Usuario Django vinculado a estas métricas.'
    )

    # --- DATOS DE IDENTIDAD ---
    
    fecha_nacimiento = models.DateField(null=True, blank=True)
    
    NIVEL_EDUCATIVO_CHOICES = [
        ('primario_completo', 'Primario Completo'),
        ('primario_incompeto', 'Primario Incompleto'),
        ('secundario_incompleto', 'Secundario Incompleto'),
        ('secundario_completo', 'Secundario Completo'),
        ('terciario_completo', 'Terciario Completo'),
        ('terciario_en_curso', 'Terciario en Curso'),
        ('terciario_incompleto', 'Terciario Incompleto'),
        ('universitario_completo', 'Universitario Completo'),
        ('universitario_en_curso', 'Universitario en Curso'),
        ('universitario_incompleto', 'Universtario Incompleto')
    ]
    nivel_educativo = models.CharField(max_length=50, choices=NIVEL_EDUCATIVO_CHOICES, blank=True)
    
    ESTADO_LABORAL_CHOICES = [
        ('activo', 'Activo'),
        ('desempleado', 'Desempleado'),
    ]
    estado_laboral = models.CharField(max_length=20, choices=ESTADO_LABORAL_CHOICES, blank=True)
        
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'), 
        #poner "otro"
        ('ND', 'Prefiero no decirlo'),
    ]
    genero = models.CharField(max_length=2, choices=GENERO_CHOICES, blank=True)

    OBJETIVO_CHOICES = [
        ('empleo', 'Mejorar oportunidades laborales'),
        ('personal', 'Desarrollo personal'),
        ('estudios', 'Apoyo para educación formal'),
        ('hobby', 'Curiosidad o pasatiempo'),
    ]
    objetivo_principal = models.CharField(max_length=20, choices=OBJETIVO_CHOICES, blank=True)

    DISPONIBILIDAD_CHOICES = [
        ('baja', 'Menos de 2 horas semanales'),
        ('media', 'Entre 2 y 5 horas semanales'),
        ('alta', 'Más de 5 horas semanales'),
    ]
    disponibilidad_tiempo = models.CharField(max_length=10, choices=DISPONIBILIDAD_CHOICES, blank=True)
    
    zona_horaria = models.CharField(
        max_length=50, 
        default='America/Argentina/Buenos_Aires',
        help_text="Zona horaria del usuario para sincronización de notificaciones y eventos."
    )
    
    intereses = models.JSONField(default=list, blank=True)

    # --- DATOS DE COMPORTAMIENTO ---
    
    frecuencia_entradas = models.PositiveIntegerField(default=0)
    racha_actual_dias = models.PositiveIntegerField(default=0)
    racha_maxima_dias = models.PositiveIntegerField(default=0)
    tiempo_acumulado_app_minutos = models.FloatField(default=0)
    tiempo_interaccion_mentor_minutos = models.FloatField(default=0)
    
    # --- DATOS DE PROGRESO ---
    
    cantidad_videos_vistos = models.PositiveIntegerField(default=0)
    tiempo_api_youtube_minutos = models.FloatField(default=0)
    desafios_completados = models.PositiveIntegerField(default=0)

    last_connection = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha y hora de la última conexión del usuario."
    )

    def __str__(self):
        return f"Métricas de Estudiante: {self.user.username}"


class UserActivityLog(models.Model):
    """
    Registro de actividad del usuario para análisis de comportamiento.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    event_type = models.CharField(max_length=50, help_text="Tipo de evento (ej. 'login', 'video_play', 'curso_completado').")
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Actividad de {self.user.username} a las {self.timestamp}"

# ── Señales — se crean automáticamente al registrar un usuario ────────────────

@receiver(post_save, sender=User)
def create_user_profile_and_config(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, role='STUDENT')
        UserConfig.objects.create(user=instance)
        StudentProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile_and_config(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    if hasattr(instance, 'config'):
        instance.config.save()
    if hasattr(instance, 'student_analytics'):
        instance.student_analytics.save()
# Campo agregado — requerido por migración 0002_userprofile_role

# ── MODELO DE PROFESORES  ────────────────

class ProfessorProfile(models.Model):
    """
    Perfil extendido exclusivo para los profesores del sistema.
    Guarda la información contractual y laboral.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='professor_profile',
        help_text='Usuario Django vinculado a este perfil docente.'
    )
    
    # 🇦🇷 Validación estricta de 8 dígitos para el DNI argentino
    from django.core.validators import RegexValidator
    dni = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(r'^\d{8}$', 'El DNI debe contener exactamente 8 números.')],
        help_text="DNI del profesor (8 dígitos numéricos)"
    )
    
    address = models.CharField(
        max_length=255,
        help_text="Dirección residencial completa"
    )

    birth_date = models.DateField(
        null=True, 
        blank=True, 
        help_text="Fecha de nacimiento del docente"
    )
    
    title_degree = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Título habilitante o especialización (Opcional)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Docente: {self.user.username} (DNI: {self.dni})"


# ── Extensión del Modelo User mediante propiedades (Buenas Prácticas) ──

@property
def is_professor(self):
    """Retorna True si el usuario tiene asignado el rol de profesor y tiene su perfil completo."""
    return hasattr(self, 'profile') and self.profile.role == 'PROFESSOR'

# Le inyectamos la propiedad dinámicamente al modelo User de Django
User.add_to_class('is_professor', is_professor)
