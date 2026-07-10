from rest_framework import serializers

class ManualCourseSerializer(serializers.Serializer):
    """
    ===========================================================================
    MÓDULO DE CARGA MANUAL - GESTIONADO POR NADIA
    ===========================================================================
    """
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255, help_text="Nombre del curso")
    description = serializers.CharField(help_text="Lo que hay en el curso")
    level = serializers.ChoiceField(choices=[('beginner', 'Principiante'), ('intermediate', 'Medio'), ('advanced', 'Avanzado')], default='beginner', help_text="Nivel: beginner, intermediate, advanced")
    discipline = serializers.CharField(max_length=100, help_text="Disciplina a la que pertenece")
    objectives = serializers.CharField(help_text="Lo que logra el alumno haciendo esto")
    cover_image = serializers.CharField(required=False, allow_blank=True, default='')
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    message = serializers.CharField(default="Curso creado exitosamente de forma manual.", read_only=True)


class AICourseSerializer(serializers.Serializer):
    """
    ===========================================================================
    MÓDULO DE INTELIGENCIA ARTIFICIAL - GESTIONADO POR GERARDO
    ===========================================================================
    """
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255, help_text="Nombre del curso")
    description = serializers.CharField(help_text="Lo que hay en el curso")
    level = serializers.ChoiceField(choices=[('beginner', 'Principiante'), ('intermediate', 'Medio'), ('advanced', 'Avanzado')], default='beginner', help_text="Nivel: beginner, intermediate, advanced")
    discipline = serializers.CharField(max_length=100, help_text="Disciplina a la que pertenece")
    objectives = serializers.CharField(help_text="Lo que logra el alumno haciendo esto")
    cover_image = serializers.CharField(required=False, allow_blank=True, default='')
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    message = serializers.CharField(default="Curso estructurado con IA exitosamente. Pendiente de revisión.", read_only=True)


class AICourseInputSerializer(serializers.Serializer):
    """
    Serializer para validar la solicitud de creación automática de cursos por IA.
    """
    objetivo_curso = serializers.CharField(
        help_text="Objetivo o tema del curso a generar con IA."
    )
    cantidad_modulos = serializers.IntegerField(
        min_value=1, max_value=10, default=3,
        help_text="Cantidad de módulos del curso (entre 1 y 10)."
    )
    generar_pdfs = serializers.BooleanField(
        default=True,
        help_text="Indica si se debe generar material de lectura PDF."
    )
    generar_cuestionarios = serializers.BooleanField(
        default=True,
        help_text="Indica si se deben generar cuestionarios de opción múltiple."
    )
    level = serializers.CharField(
        required=False, default='beginner',
        help_text="Nivel del estudiante ('beginner', 'intermediate' o 'advanced')."
    )
    discipline = serializers.CharField(
        required=False, default='general',
        help_text="Disciplina o categoría del curso."
    )
    learning_objectives = serializers.CharField(
        required=False, allow_blank=True, default='',
        help_text="Objetivos de aprendizaje específicos provistos por el profesor."
    )
    cover_image = serializers.CharField(
        required=False, allow_blank=True, default='',
        help_text="URL de la imagen de portada opcional."
    )


class LessonDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    duration = serializers.CharField()
    resource_type = serializers.CharField()
    resource_url = serializers.CharField()
    transcription = serializers.CharField()
    order = serializers.IntegerField()


class ModuleDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    order = serializers.IntegerField()
    has_quiz = serializers.BooleanField(required=False, default=False)
    lessons = LessonDetailSerializer(many=True, read_only=True)
    quiz = serializers.SerializerMethodField(required=False)

    def get_quiz(self, obj):
        quizzes = self.context.get('quizzes', {})
        module_id = obj.get('id') if isinstance(obj, dict) else getattr(obj, 'id', None)
        return quizzes.get(module_id, [])


class AICourseDetailResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField()
    level = serializers.CharField()
    discipline = serializers.CharField()
    objectives = serializers.CharField()
    cover_image = serializers.CharField()
    professor = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField()
    message = serializers.CharField(default="Curso estructurado con IA exitosamente. Pendiente de revisión.", read_only=True)
    modules = ModuleDetailSerializer(many=True, read_only=True)


class LessonRatingSerializer(serializers.Serializer):
    rating = serializers.IntegerField(
        min_value=1, max_value=5, required=True,
        help_text="Calificación de la clase (1 a 5 estrellas)."
    )


class QuizAnswerSerializer(serializers.Serializer):
    question_index = serializers.IntegerField(help_text="Índice de la pregunta.")
    selected_option_index = serializers.IntegerField(help_text="Índice de la opción seleccionada.")


class QuizSubmitSerializer(serializers.Serializer):
    answers = QuizAnswerSerializer(many=True, help_text="Lista de respuestas enviadas.")


class WrongQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    question_text = serializers.CharField()
    selected_option = serializers.CharField()
    correct_option = serializers.CharField()
    created_at = serializers.DateTimeField()


class StudentCourseStateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    student_username = serializers.CharField(read_only=True)
    course_title = serializers.CharField(read_only=True)
    current_module_title = serializers.CharField(read_only=True)
    current_lesson_title = serializers.CharField(read_only=True)
    progress_percent = serializers.FloatField()
    global_frustration = serializers.IntegerField()
    is_completed = serializers.BooleanField()
    started_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(allow_null=True)
    total_time_spent = serializers.DurationField(allow_null=True)
    last_activity = serializers.DateTimeField()
    inactivity_alert_sent = serializers.BooleanField()