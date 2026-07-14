from rest_framework import serializers

class CourseAvailableListSerializer(serializers.Serializer):
    """
    DTO para listar los cursos activos disponibles para inscripcion.
    """
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    level = serializers.CharField()
    discipline = serializers.CharField()
    objectives = serializers.CharField()
    cover_image = serializers.CharField()
    professor_name = serializers.CharField(read_only=True)


class EnrollmentCreateSerializer(serializers.Serializer):
    """
    DTO de entrada para procesar la solicitud de una nueva inscripcion.
    """
    course_id = serializers.IntegerField(required=True, help_text="ID of the course to enroll in.")


class EnrolledCourseDetailSerializer(serializers.Serializer):
    """
    DTO secundario para mostrar el detalle del curso e indirectamente su profesor.
    """
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    professor_name = serializers.CharField()
    enrolled_at = serializers.DateTimeField()


class StudentDashboardSerializer(serializers.Serializer):
    """
    DTO principal para devolver el perfil del alumno y todos sus cursos ligados.
    """
    student_id = serializers.IntegerField()
    student_username = serializers.CharField()
    student_email = serializers.CharField()
    enrolled_courses_count = serializers.IntegerField()
    enrolled_courses = EnrolledCourseDetailSerializer(many=True)