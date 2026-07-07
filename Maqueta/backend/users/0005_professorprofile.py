# Generated manually — extrae SOLO el CreateModel(ProfessorProfile) que la
# rama courses-ger-ia traía embebido (incorrectamente) dentro de una copia
# reescrita de 0003. No se toca 0003 ni 0004 porque ya están aplicadas en
# entornos existentes y Django las trackea por nombre de archivo, no por
# contenido — reescribirlas no las re-ejecuta donde ya corrieron.

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_studentprofile_tiempo_acumulado_app_minutos_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfessorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dni', models.CharField(help_text='DNI del profesor (8 dígitos numéricos)', max_length=8, unique=True, validators=[django.core.validators.RegexValidator('^\\d{8}$', 'El DNI debe contener exactamente 8 números.')])),
                ('address', models.CharField(help_text='Dirección residencial completa', max_length=255)),
                ('birth_date', models.DateField(blank=True, help_text='Fecha de nacimiento del docente', null=True)),
                ('title_degree', models.CharField(blank=True, help_text='Título habilitante o especialización (Opcional)', max_length=150, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(help_text='Usuario Django vinculado a este perfil docente.', on_delete=django.db.models.deletion.CASCADE, related_name='professor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
