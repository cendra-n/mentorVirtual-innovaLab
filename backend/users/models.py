"""
users/models.py

UserProfile  — datos de perfil (phone, avatar_url, bio_face_hash para biometría futura)
UserConfig   — preferencias de accesibilidad (font_size, high_contrast, voice_guidance)

Ambos se crean automáticamente via señales al crear un User.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile',
        help_text="Usuario Django propietario de este perfil."
    )
    bio_face_hash = models.TextField(
        null=True, blank=True,
        help_text="Hash/embedding del rostro para autenticación biométrica (Fase 3)."
    )
    avatar_url = models.CharField(
        max_length=255, blank=True,
        help_text="URL de la imagen de avatar del usuario."
    )
    phone = models.CharField(
        max_length=50, blank=True,
        help_text="Número telefónico de contacto."
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


# ── Señales — se crean automáticamente al registrar un usuario ────────────────

@receiver(post_save, sender=User)
def create_user_profile_and_config(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserConfig.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile_and_config(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    if hasattr(instance, 'config'):
        instance.config.save()
