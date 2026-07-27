"""
users/models.py

UserProfile  — datos de perfil (phone, avatar_url, bio_face_hash para biometría futura)
UserConfig   — preferencias de accesibilidad (font_size, high_contrast, voice_guidance)
StudentProfile — métricas, progreso y comportamiento para análisis de datos.

Ambos se crean automáticamente via señales al crear un User.
"""
import threading
import logging
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

logger = logging.getLogger('users')

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
    
    birth_date = models.DateField(null=True, blank=True)
    
    EDUCATION_LEVEL_CHOICES = [
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
    education_level = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES, blank=True)
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('desempleado', 'Desempleado'),
    ]
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, blank=True)
        
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'), 
        #poner "otro"
        ('ND', 'Prefiero no decirlo'),
    ]
    user_gender = models.CharField(max_length=2, choices=GENDER_CHOICES, blank=True)

    PRIMARY_OBJECTIVE_CHOICES = [
        ('empleo', 'Mejorar oportunidades laborales'),
        ('personal', 'Desarrollo personal'),
        ('estudios', 'Apoyo para educación formal'),
        ('hobby', 'Curiosidad o pasatiempo'),
    ]
    primary_objective = models.CharField(max_length=20, choices=PRIMARY_OBJECTIVE_CHOICES, blank=True)

    TIME_AVAILABILITY_CHOICES = [
        ('baja', 'Menos de 2 horas semanales'),
        ('media', 'Entre 2 y 5 horas semanales'),
        ('alta', 'Más de 5 horas semanales'),
    ]
    time_availability = models.CharField(max_length=10, choices=TIME_AVAILABILITY_CHOICES, blank=True)
    
    time_zone = models.CharField(
        max_length=50, 
        default='America/Argentina/Buenos_Aires',
        help_text="Zona horaria del usuario para sincronización de notificaciones y eventos."
    )
    
    user_interests = models.JSONField(default=list, blank=True)

    # --- DATOS DE COMPORTAMIENTO ---
    
    entry_frequency = models.PositiveIntegerField(default=0)
    current_streak_days = models.PositiveIntegerField(default=0)
    max_streak_days = models.PositiveIntegerField(default=0)
    app_time_min = models.FloatField(default=0)
    mentor_interaction_time_min = models.FloatField(default=0)
    
    # --- DATOS DE PROGRESO ---
    
    watched_videos_count = models.PositiveIntegerField(default=0)
    youtube_api_time_min = models.FloatField(default=0)
    completed_challenges = models.PositiveIntegerField(default=0)

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


# ── Email de bienvenida post-registro ───────────────────────────────────────
@receiver(post_save, sender=User)
def send_email_post_register(sender, instance, created, **kwargs):
    """Envía un mail de bienvenida al crear un User. Corre en un hilo aparte
    para no bloquear la respuesta del registro con la latencia del SMTP."""
    if not created:
        return

    subject = 'Bienvenido a Mentor Virtual'
    message = f'Hola {instance.username}, tu registro ha sido exitoso.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [instance.email]

    def send_async():
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            logger.info(f"Email de bienvenida enviado a {instance.email}")
        except Exception as e:
            logger.error(
                f"Fallo al enviar email de bienvenida a {instance.email}: {e}",
                exc_info=True
            )

    threading.Thread(target=send_async, daemon=True).start()
