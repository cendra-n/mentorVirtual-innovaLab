from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Principiante'),
        ('intermediate', 'Medio'),
        ('advanced', 'Avanzado'),
    ]

    professor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='courses_managed',
        help_text="Usuario con rol PROFESSOR propietario de este curso."
    )
    
    title = models.CharField(max_length=255, help_text="Título del curso.")
    description = models.TextField(blank=True, default="", help_text="Descripción general.")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner', help_text="Nivel de dificultad.")
    discipline = models.CharField(max_length=100, blank=True, default="general", help_text="Disciplina a la que pertenece.")
    objectives = models.TextField(blank=True, default="", help_text="¿Qué logrará el alumno?")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False, help_text="Indica si el curso está activo.")
    cover_image = models.TextField(blank=True, default="", help_text="URL o data-URI (base64) de la imagen de portada.")
    
    class Meta:
        db_table = 'courses'

    def __str__(self):
        nombre_limpio = self.professor.username.replace('.', ' ') if self.professor else "Sin Profesor"
        return nombre_limpio


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255, help_text="Nombre del bloque.")
    order = models.PositiveIntegerField(default=1, db_column='module_order')

    class Meta:
        db_table = 'course_modules'
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} -> {self.title}"


class Lesson(models.Model):
    RESOURCE_CHOICES = [
        ('PDF', 'Documento de Lectura (PDF)'),
        ('YTB', 'Video de YouTube'),
    ]
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255, help_text="Título de la lección.")
    duration = models.CharField(max_length=50, blank=True, default="15 minutos")
    resource_type = models.CharField(max_length=3, choices=RESOURCE_CHOICES, default='PDF')
    resource_url = models.URLField(blank=True, default="")
    transcription = models.TextField(blank=True, default="", help_text="Transcripción del video o texto completo para lectores de pantalla.")
    order = models.PositiveIntegerField(default=1, db_column='lesson_order')

    class Meta:
        db_table = 'course_lessons'
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} -> {self.title}"


class LessonProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True, help_text="Puntuación dada (1 a 5 estrellas)")
    attempts = models.PositiveIntegerField(default=0, help_text="Intentos de realización de esta lección o su cuestionario")
    frustration_level = models.IntegerField(default=0, help_text="Nivel de frustración estimado para esta lección (0 a 5)")

    class Meta:
        db_table = 'lesson_progress'
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student.username} -> {self.lesson.title} ({'Completada' if self.is_completed else 'Pendiente'})"


class QuizAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.FloatField(help_text="Porcentaje de respuestas correctas (0.0 a 100.0)")
    passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quiz_attempts'

    def __str__(self):
        return f"{self.student.username} -> Módulo {self.module.title} (Score: {self.score}%, {'Aprobado' if self.passed else 'Reprobado'})"


class WrongQuestion(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wrong_questions')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='wrong_questions')
    question_text = models.TextField(help_text="Texto de la pregunta que fue contestada de forma incorrecta.")
    selected_option = models.CharField(max_length=255, help_text="Opción que seleccionó el estudiante.")
    correct_option = models.CharField(max_length=255, help_text="Opción correcta de la pregunta.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wrong_questions'

    def __str__(self):
        return f"{self.student.username} -> Pregunta errada en Módulo {self.module.id}"


class StudentCourseState(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_states')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_states')
    current_module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True)
    current_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    progress_percent = models.FloatField(default=0.0, help_text="Porcentaje de avance general del curso (0.0 a 100.0)")
    global_frustration = models.IntegerField(default=0, help_text="Nivel de frustración general estimado (0 a 5)")
    is_completed = models.BooleanField(default=False, help_text="Indica si el estudiante finalizó el curso.")
    started_at = models.DateTimeField(auto_now_add=True, help_text="Fecha en que el alumno inició el curso.")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="Fecha en que el alumno completó el curso.")
    total_time_spent = models.DurationField(null=True, blank=True, help_text="Tiempo total empleado para culminar el curso.")
    last_activity = models.DateTimeField(auto_now=True, help_text="Fecha de la última interacción del estudiante con el curso.")
    inactivity_alert_sent = models.BooleanField(default=False, help_text="Evita duplicar alertas de inactividad enviadas.")

    class Meta:
        db_table = 'student_course_state'
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} -> Estado en {self.course.title}"