from rest_framework import serializers

#serializer para la lista de cursos activados, lo ven los 3 roles
class CourseAvailableListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    professor_name = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    level = serializers.CharField()
    discipline = serializers.CharField()
    objectives = serializers.CharField()
    cover_image = serializers.CharField(allow_null=True)
    
  #serializer para que el alumno se anote a cursos, solo disponible para alumnos  
class EnrollmentCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=True, help_text="ID del curso al que desea inscribirse.")

#serializer para la lista de inscriptos el admin ve todo, el profesor solo lo relacionado a él y el alumno no puede entrar
class EnrollmentListSerializer(serializers.Serializer):
    enrollment_id = serializers.IntegerField()
    student_email = serializers.EmailField()
    course_name = serializers.CharField()
    professor_name = serializers.CharField()

#serializer para la lista de cursos de cada alumno en particular, solo puede entrar el rol estudiante

class EnrollmentListSerializerStudent(serializers.Serializer):
    """
    Serializador para la lista de inscripciones (Mis Cursos).
    """
    enrollment_id = serializers.IntegerField(help_text="ID único de la inscripción")
    student_email = serializers.EmailField(help_text="Correo electrónico del estudiante")
    course_name = serializers.CharField(max_length=255, help_text="Nombre del curso")
    professor_name = serializers.CharField(max_length=255, help_text="Nombre del profesor")

    class Meta:
        # Esto ayuda a drf-spectacular a generar el esquema correctamente
        fields = ['enrollment_id', 'student_email', 'course_name', 'professor_name']