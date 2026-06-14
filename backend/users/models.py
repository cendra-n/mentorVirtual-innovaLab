from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN',     'Administrador'),
        ('STUDENT',   'Alumno'),
        ('PROFESSOR', 'Profesor'),
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile',
        help_text="Usuario Django propietario de este perfil."
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='STUDENT',
        help_text="Rol del usuario en la plataforma."
    )
    bio_face_hash = models.TextField(
        null=True, blank=True,
        help_text="Hash/embedding del rostro para autenticación biométrica (Fase 3)."
    )
    avatar_url = models.CharField(max_length=255, blank=True)
    phone      = models.CharField(max_length=50,  blank=True)

    def save(self, *args, **kwargs):
        if self.user.is_superuser or self.user.is_staff:
            self.role = 'ADMIN'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class UserConfig(models.Model):
    FONT_SIZE_CHOICES = [('SMALL','Small'),('MEDIUM','Medium'),('LARGE','Large')]
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name='config')
    font_size      = models.CharField(max_length=10, choices=FONT_SIZE_CHOICES, default='MEDIUM')
    high_contrast  = models.BooleanField(default=False)
    voice_guidance = models.BooleanField(default=False)

    def __str__(self):
        return f"Configuración de {self.user.username}"


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
