from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

class QuizQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, help_text="Texto de la pregunta.")
    options = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="Lista de opciones de respuesta (mínimo 2)."
    )
    correct_option_index = serializers.IntegerField(
        required=True,
        help_text="Índice de la opción correcta (basado en 0)."
    )


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

    @extend_schema_field(QuizQuestionSerializer(many=True))
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
    message = serializers.SerializerMethodField(read_only=True)
    modules = ModuleDetailSerializer(many=True, read_only=True)

    def get_message(self, obj):
        gen_type = obj.get('generation_type') if isinstance(obj, dict) else getattr(obj, 'generation_type', 'ai')
        if gen_type == 'manual':
            return "Curso creado exitosamente de forma manual."
        return "Curso estructurado con IA exitosamente. Pendiente de revisión."


class LessonCreationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=True, help_text="Título de la lección.")
    duration = serializers.CharField(max_length=50, required=True, help_text="Duración de la lección (ej: '15 minutos').")
    resource_type = serializers.ChoiceField(choices=[('PDF', 'PDF'), ('YTB', 'YTB')], default='PDF', help_text="Tipo de recurso (PDF o YTB).")
    resource_url = serializers.URLField(required=True, help_text="URL del recurso/material.")
    transcription = serializers.CharField(required=False, allow_blank=True, default='', help_text="Transcripción opcional.")
    order = serializers.IntegerField(required=False, default=1, help_text="Orden de la lección.")


class ModuleCreationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=True, help_text="Título del módulo.")
    order = serializers.IntegerField(required=False, default=1, help_text="Orden del módulo.")
    lessons = LessonCreationSerializer(many=True, required=True, help_text="Lecciones del módulo (mínimo 1).")
    quiz = QuizQuestionSerializer(many=True, required=False, default=list, help_text="Preguntas del cuestionario.")

    def validate_lessons(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("El módulo debe contener al menos una lección.")
        return value


class CourseCreationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255, required=True, help_text="Título del curso.")
    description = serializers.CharField(required=False, allow_blank=True, default="", help_text="Descripción del curso.")
    level = serializers.ChoiceField(
        choices=[('beginner', 'Principiante'), ('intermediate', 'Medio'), ('advanced', 'Avanzado'),
                 ('principiante', 'Principiante'), ('medio', 'Medio'), ('avanzado', 'Avanzado'), ('alto', 'Alto')],
        default='beginner',
        help_text="Nivel de dificultad."
    )
    discipline = serializers.CharField(max_length=100, required=False, default="general", help_text="Disciplina.")
    objectives = serializers.CharField(required=False, allow_blank=True, default="", help_text="Objetivos.")
    cover_image = serializers.CharField(required=False, allow_blank=True, default="", help_text="URL de portada.")
    modules = ModuleCreationSerializer(many=True, required=False, default=list, help_text="Módulos del curso.")

    def create(self, validated_data):
        from django.db import transaction
        from django.conf import settings
        from courses import db

        professor = self.context['request'].user
        modules_data = validated_data.pop('modules', [])

        with transaction.atomic():
            course_id = db.create_course_manual(
                professor_id=professor.id,
                title=validated_data['title'],
                description=validated_data.get('description', ''),
                level=validated_data.get('level', 'beginner'),
                discipline=validated_data.get('discipline', 'general'),
                objectives=validated_data.get('objectives', ''),
                cover_image=validated_data.get('cover_image', ''),
                max_courses=settings.MAX_COURSES_PER_PROFESSOR
            )

            for m_idx, m_data in enumerate(modules_data, 1):
                m_title = m_data['title'].strip()
                m_order = m_data.get('order', m_idx)
                module_id = db.add_module(course_id, m_title, m_order)

                lessons_data = m_data.get('lessons', [])
                for l_idx, l_data in enumerate(lessons_data, 1):
                    db.add_lesson(
                        module_id,
                        l_data['title'],
                        l_data.get('duration', '15 minutos'),
                        l_data.get('resource_type', 'PDF'),
                        l_data.get('resource_url', ''),
                        l_data.get('transcription', ''),
                        l_data.get('order', l_idx)
                    )

                quiz_data = m_data.get('quiz')
                if quiz_data:
                    if len(quiz_data) < 2:
                        raise serializers.ValidationError(
                            f"El cuestionario del Módulo '{m_title}' debe contener al menos 2 preguntas."
                        )
                    quiz_data_plain = []
                    for q_idx, qItem in enumerate(quiz_data):
                        question_text = qItem.get('question', '').strip()
                        if not question_text:
                            raise serializers.ValidationError(
                                f"La pregunta {q_idx + 1} del cuestionario del Módulo '{m_title}' no puede estar vacía."
                            )
                        options = qItem.get('options', [])
                        if len(options) < 2:
                            raise serializers.ValidationError(
                                f"La pregunta {q_idx + 1} del cuestionario del Módulo '{m_title}' debe tener al menos 2 opciones."
                            )
                        for o_idx, opt in enumerate(options):
                            if not str(opt).strip():
                                raise serializers.ValidationError(
                                    f"La opción {o_idx + 1} de la pregunta {q_idx + 1} del cuestionario del Módulo '{m_title}' no puede estar vacía."
                                )
                        correct_idx = qItem.get('correct_option_index')
                        if correct_idx is None or correct_idx < 0 or correct_idx >= len(options):
                            raise serializers.ValidationError(
                                f"Selecciona la respuesta correcta para la pregunta {q_idx + 1} del cuestionario del Módulo '{m_title}'."
                            )
                        quiz_data_plain.append({
                            "question": question_text,
                            "options": [str(o).strip() for o in options],
                            "correct_option_index": correct_idx
                        })
                    db.save_module_quiz(module_id, quiz_data_plain)

            return {
                "id": course_id,
                "title": validated_data['title'],
                "description": validated_data.get('description', ''),
                "level": validated_data.get('level', 'beginner'),
                "discipline": validated_data.get('discipline', 'general'),
                "objectives": validated_data.get('objectives', ''),
                "cover_image": validated_data.get('cover_image', ''),
                "generation_type": "manual"
            }


class ModuleCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=True, help_text="ID del curso asociado.")
    title = serializers.CharField(max_length=255, required=True, help_text="Título del módulo.")
    order = serializers.IntegerField(required=False, allow_null=True)

    def validate_course_id(self, value):
        from courses import db
        course = db.get_course_detail(value)
        if not course:
            raise serializers.ValidationError("Curso no encontrado.")
        return value



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