from django.db import models
from django.contrib.auth.models import User
from courses.models import Course  # Importación limpia del modelo Course existente

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('completed', 'Completado'),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Estudiante inscrito en el curso."
    )
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Curso en el que se inscribe el estudiante."
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Estado de la inscripción del alumno."
    )
    
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora exactas de la inscripción."
    )

    class Meta:
        db_table = 'enrollment_enrollment'
        unique_together = ('student', 'course')

    def __str__(self):
        student_name = self.student.username if self.student else "Sin Estudiante"
        course_title = self.course.title if self.course else "Sin Curso"
        return f"{student_name} -> {course_title} ({self.status})"