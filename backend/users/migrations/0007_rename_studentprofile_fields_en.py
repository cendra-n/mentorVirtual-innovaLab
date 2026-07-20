# Refactor: nombres de columna de StudentProfile de español a inglés.
# RenameField renombra el field de Django Y la columna real en Postgres
# (no hay db_column explícito en el modelo, así que no hace falta SQL crudo).
# Coordinar con Nadia (cendra) antes de mergear: toca la tabla users_studentprofile,
# que puede tener migraciones pendientes en feature-courses.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_geo_entities_and_activity_log'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studentprofile',
            old_name='fecha_nacimiento',
            new_name='birth_date',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='nivel_educativo',
            new_name='education_level',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='estado_laboral',
            new_name='employment_status',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='genero',
            new_name='user_gender',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='objetivo_principal',
            new_name='primary_objective',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='disponibilidad_tiempo',
            new_name='time_availability',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='zona_horaria',
            new_name='time_zone',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='intereses',
            new_name='user_interests',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='frecuencia_entradas',
            new_name='entry_frequency',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='racha_actual_dias',
            new_name='current_streak_days',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='racha_maxima_dias',
            new_name='max_streak_days',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='tiempo_acumulado_app_minutos',
            new_name='app_time_min',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='tiempo_interaccion_mentor_minutos',
            new_name='mentor_interaction_time_min',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='cantidad_videos_vistos',
            new_name='watched_videos_count',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='tiempo_api_youtube_minutos',
            new_name='youtube_api_time_min',
        ),
        migrations.RenameField(
            model_name='studentprofile',
            old_name='desafios_completados',
            new_name='completed_challenges',
        ),
    ]
