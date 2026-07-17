from rest_framework import serializers


class CourseAvailableListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    professor_name = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    level = serializers.CharField()
    discipline = serializers.CharField()
    objectives = serializers.CharField()
    cover_image = serializers.CharField(allow_null=True)
    
    
class EnrollmentCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=True, help_text="ID del curso al que desea inscribirse.")


class EnrollmentListSerializer(serializers.Serializer):
    enrollment_id = serializers.IntegerField()
    student_email = serializers.EmailField()
    course_name = serializers.CharField()
    professor_name = serializers.CharField()
