import os
from django.db import migrations

def load_stored_procedures(apps, schema_editor):
    from django.conf import settings
    
    # 1. Ejecutar backend/init.sql (tutor y metas)
    init_sql_path = os.path.join(settings.BASE_DIR, 'init.sql')
    if os.path.exists(init_sql_path):
        with open(init_sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            with schema_editor.connection.cursor() as cursor:
                cursor.execute(sql_content)

    # 2. Ejecutar backend/courses/init_courses.sql (cursos, módulos, lecciones y SPs de cursos)
    courses_sql_path = os.path.join(settings.BASE_DIR, 'courses', 'init_courses.sql')
    if os.path.exists(courses_sql_path):
        with open(courses_sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            with schema_editor.connection.cursor() as cursor:
                cursor.execute(sql_content)

def unload_stored_procedures(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_alter_course_professor'),
    ]

    operations = [
        migrations.RunPython(load_stored_procedures, reverse_code=unload_stored_procedures),
    ]
