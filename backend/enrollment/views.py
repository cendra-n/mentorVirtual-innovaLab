from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema

# Importamos nuestro archivo de base de datos y los serializadores
from enrollment import db as enrollment_db
from enrollment.serializers import (
    CourseAvailableListSerializer, 
    EnrollmentCreateSerializer, 
    StudentDashboardSerializer
)

class AvailableCoursesAPIView(APIView):
    """
    Vista de la API para que los alumnos listen los cursos disponibles.
    """
    permission_classes = [permissions.IsAuthenticated] # Requiere token de autenticacion

    @extend_schema(
        summary="List available courses",
        description="Devuelve una lista de todos los cursos activos que han sido aprobados por el administrador.",
        responses={200: CourseAvailableListSerializer(many=True)}
    )
    def get(self, request):
        # Llamamos a la query nativa de db.py
        courses = enrollment_db.get_available_courses()
        # Pasamos el resultado por el Serializer (DTO)
        serializer = CourseAvailableListSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EnrollStudentAPIView(APIView):
    """
    Vista de la API para procesar la inscripcion de un alumno a un curso.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Enroll in a course",
        description="Inscribe al alumno autenticado en un curso activo. Valida el limite maximo de 3 cursos.",
        request=EnrollmentCreateSerializer,
        responses={
            201: {"description": "Successfully enrolled"},
            400: {"description": "Validation error (Course inactive, duplicate, or limit reached)"}
        }
    )
    def post(self, request):
        # Validamos el cuerpo de la peticion (body JSON)
        serializer = EnrollmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Tomamos el ID del alumno logueado directamente del token/request
        student_id = request.user.id
        course_id = serializer.validated_data['course_id']
        
        # Ejecutamos la transaccion en la base de datos
        enrollment_id = enrollment_db.enroll_student_in_course(student_id, course_id)
        
        return Response(
            {
                "message": "Successfully enrolled in the course.",
                "enrollment_id": enrollment_id
            },
            status=status.HTTP_201_CREATED
        )


class StudentDashboardAPIView(APIView):
    """
    Vista de la API para ver el perfil del alumno y sus cursos enlazados con sus profesores.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get student dashboard data",
        description="Devuelve el perfil del alumno y la lista detallada de sus cursos inscritos con el nombre del profesor.",
        responses={200: StudentDashboardSerializer}
    )
    def get(self, request):
        student_id = request.user.id
        
        # Obtenemos el diccionario estructurado desde la base de datos
        dashboard_data = enrollment_db.get_student_dashboard_data(student_id)
        
        if not dashboard_data:
            return Response({"detail": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)
            
        # Serializamos la respuesta final
        serializer = StudentDashboardSerializer(dashboard_data)
        return Response(serializer.data, status=status.HTTP_200_OK)