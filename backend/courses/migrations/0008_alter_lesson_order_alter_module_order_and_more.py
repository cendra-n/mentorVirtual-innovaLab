from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_stored_procedures'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='lesson',
                    name='order',
                    field=models.PositiveIntegerField(default=1, db_column='lesson_order'),
                ),
                migrations.AlterField(
                    model_name='module',
                    name='order',
                    field=models.PositiveIntegerField(default=1, db_column='module_order'),
                ),
                migrations.AlterModelTable(name='course', table='courses'),
                migrations.AlterModelTable(name='module', table='course_modules'),
                migrations.AlterModelTable(name='lesson', table='course_lessons'),
                migrations.AlterModelTable(name='lessonprogress', table='lesson_progress'),
                migrations.AlterModelTable(name='quizattempt', table='quiz_attempts'),
                migrations.AlterModelTable(name='wrongquestion', table='wrong_questions'),
                migrations.AlterModelTable(name='studentcoursestate', table='student_course_state'),
            ],
            database_operations=[],
        ),
    ]
