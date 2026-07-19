import os
from django.db import migrations


def load_stored_procedures(apps, schema_editor):
    from django.conf import settings

    # Ejecutar backend/enrollment/init_enrollment.sql (tabla + SPs de inscripciones).
    # OJO: nunca uses schema_editor.execute() acá — interpreta '%' como
    # placeholder de parámetro (mogrify de psycopg) y revienta con IndexError.
    # Por eso se usa el cursor crudo, igual que en courses/0007_stored_procedures.py.
    enrollment_sql_path = os.path.join(settings.BASE_DIR, 'enrollment', 'init_enrollment.sql')
    if os.path.exists(enrollment_sql_path):
        with open(enrollment_sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            with schema_editor.connection.cursor() as cursor:
                cursor.execute(sql_content)


def unload_stored_procedures(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_stored_procedures, reverse_code=unload_stored_procedures),
    ]
