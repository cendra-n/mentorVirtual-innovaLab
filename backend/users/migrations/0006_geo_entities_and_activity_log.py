import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Integra la parte aditiva del trabajo de geo/analítica de Paula
    (entidades geográficas, UserActivityLog, campos de residencia/sesión
    en UserProfile) sobre develop.

    A diferencia de su migración original (0006_country_locality_nationality_and_more.py,
    en su rama), esta NO incluye los RemoveField/RenameField sobre StudentProfile
    (fecha_nacimiento -> birth_date, remoción de racha_actual_dias/tiempo_acumulado_app_minutos/
    etc.) — esos campos ya existen en producción con datos reales, no se tocan.
    StudentProfile se deja completamente intacto.
    """

    dependencies = [
        ('users', '0005_professor_profile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('nationality_id', models.AutoField(primary_key=True, serialize=False)),
                ('nationality_name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Nacionalidad',
                'verbose_name_plural': 'Nacionalidades',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('country_id', models.AutoField(primary_key=True, serialize=False)),
                ('country_name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'País',
                'verbose_name_plural': 'Países',
            },
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('province_id', models.AutoField(primary_key=True, serialize=False)),
                ('province_name', models.CharField(max_length=100, unique=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provinces', to='users.country')),
            ],
            options={
                'verbose_name': 'Provincia',
                'verbose_name_plural': 'Provincias',
            },
        ),
        migrations.CreateModel(
            name='Locality',
            fields=[
                ('locality_id', models.AutoField(primary_key=True, serialize=False)),
                ('locality_name', models.CharField(max_length=100)),
                ('province', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='localities', to='users.province')),
            ],
            options={
                'verbose_name': 'Localidad',
                'verbose_name_plural': 'Localidades',
            },
        ),
        migrations.AlterUniqueTogether(
            name='locality',
            unique_together={('locality_name', 'province')},
        ),
        migrations.CreateModel(
            name='UserActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(help_text="Tipo de evento (ej. 'login', 'video_play', 'curso_completado').", max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='nationality',
            field=models.ForeignKey(blank=True, help_text='Nacionalidad del usuario.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.nationality'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='country_residence',
            field=models.ForeignKey(blank=True, help_text='País de residencia del usuario.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.country'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='province_residence',
            field=models.ForeignKey(blank=True, help_text='Provincia de residencia del usuario.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.province'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='locality_residence',
            field=models.ForeignKey(blank=True, help_text='Localidad de residencia del usuario.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.locality'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='internet_access',
            field=models.BooleanField(default=True, help_text='Indica si el usuario tiene acceso a internet.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='session_status',
            field=models.CharField(choices=[('ONLINE', 'Online'), ('OFFLINE', 'Offline')], default='OFFLINE', max_length=10),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='last_connection',
            field=models.DateTimeField(blank=True, help_text='Fecha y hora de la última conexión del usuario.', null=True),
        ),
    ]
