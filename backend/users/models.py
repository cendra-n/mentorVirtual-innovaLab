from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# class UserProfile(models.Model):
    
#     user = models.OneToOneField(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name='profile',
#         help_text="Usuario Django propietario de este perfil."
#     )
    
#     # El hash biométrico queda como opcional (null=True, blank=True) para más adelante
#     # bio_face_hash = models.TextField(null=True, blank=True) 
#     avatar_url = models.CharField(
#         max_length=255, 
#         blank=True,
#         help_text="URL de la imagen de avatar o foto de perfil del usuario."
#     )
#     phone = models.CharField(
#         max_length=50, 
#         blank=True,
#         help_text="Número telefónico de contacto del usuario."
#     )       
    
#     def __str__(self):
#         return f"Perfil de {self.user.username}"
   
class UserProfile(AbstractUser):
    # Opciones de roles según la documentación
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('STUDENT', 'Alumno'),
        ('PROFESSOR', 'Profesor'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')

    bio_face_hash = models.CharField(max_length=255, blank=True, null=True)
    accessibility_settings = models.JSONField(default=dict, blank=True)
    abandonment_reason = models.TextField(blank=True, null=True)
    time_since_abandonment = models.CharField(max_length=100, blank=True, null=True)
    security_shield_level = models.IntegerField(default=0)
    
    phone = models.CharField(max_length=50, blank=True)       
    avatar_url = models.CharField(max_length=255, blank=True)
    
    def save(self, *args, **kwargs):
        # Automatización: Si en consola o admin se marca como superusuario,
        # le asignamos automáticamente el rol jerárquico 'ADMIN'
        if self.is_superuser or self.is_staff:
            self.role = 'ADMIN'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
class UserConfig(models.Model):
    
    # Opciones para el ENUM de font_size
    FONT_SIZE_CHOICES = [
        ('SMALL', 'Small'),
        ('MEDIUM', 'Medium'),
        ('LARGE', 'Large'),
    ]

    user = models.OneToOneField(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='config',
        help_text="Usuario propietario de esta configuración."
    )
    font_size = models.CharField(
        max_length=10, 
        choices=FONT_SIZE_CHOICES, 
        default='MEDIUM',
        help_text="Tamaño de la tipografía preferida por el usuario para accesibilidad ('SMALL', 'MEDIUM', 'LARGE')."
    )
    high_contrast = models.BooleanField(
        default=False,
        help_text="Preferencia de visualización de colores con contraste elevado para accesibilidad."
    )
    voice_guidance = models.BooleanField(
        default=False,
        help_text="Preferencia de navegación asistida por comandos y locución de voz."
    )

    def __str__(self):
        return f"Configuración de {self.user.username}"
    


# Señal automatizada para mantener el UserConfig siempre acoplado al crear un usuario
@receiver(post_save, sender=UserProfile)
def create_user_config(sender, instance, created, **kwargs):
    if created:  
        UserConfig.objects.create(user=instance)

@receiver(post_save, sender=UserProfile)
def save_user_config(sender, instance, **kwargs):
    if hasattr(instance, 'config'):
        instance.config.save()