from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from drf_spectacular.utils import extend_schema 
from rest_framework import status
from enrollment.permissions import IsOwnerOrAdmin
from .permissions import get_user_role  
from .db import get_available_courses
from .db import enroll_student_in_course
from .db import get_all_enrollments_db
from .serializers import CourseAvailableListSerializer, EnrollmentCreateSerializer
from .serializers import EnrollmentListSerializer
from .pagination import StandardResultsSetPagination

#------------------GET/coursesActive
class AvailableCoursesAPIView(APIView):
    #Los 3 roles pueden ver la lista de cursos activos solo se valida que la persona este logeada
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Lista de cursos disponibles",
        description="Devuelve una lista de todos los cursos activos.",
        responses={200: CourseAvailableListSerializer(many=True)}
    )
    def get(self, request):
        # 1. Obtener la lista cruda
        courses = get_available_courses()
        
        # 2. Paginar
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(courses, request, view=self)
        
        if page is not None:
            serializer = CourseAvailableListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        serializer = CourseAvailableListSerializer(courses, many=True)
        return Response(serializer.data)
        

#------------------Post/enrollmentStudent
class EnrollStudentAPIView(APIView):
    """
    Vista de la API para procesar la inscripción de un alumno a un curso.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Inscripción a cursos disponibles",
        description="El alumno autenticado puede anotarse a los cursos disponibles. Valida el límite máximo de 3 cursos en la versión MVP.",
        request=EnrollmentCreateSerializer,
        responses={
            201: {"description": "Felicidades te has inscripto correctamente al curso"},
            400: {"description": "Error al inscribirse)"}
        }
    )
    def post(self, request):
        # 1. Validación de ROL accediendo al perfil relacionado
        try:
            user_role = request.user.profile.role 
        except AttributeError:
            return Response(
                {"detail": "Error: usuario sin perfil de alumno asignado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_role != 'STUDENT':
            return Response(
                {"detail": "Error: solo puedes anotarte si tu rol es estudiante."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. Validación de Serializer
        serializer = EnrollmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 3. Resto de tu lógica...
        student_id = request.user.id
        course_id = serializer.validated_data['course_id']
        
        enrollment_id = enroll_student_in_course(student_id, course_id)
        
        return Response(
            {
                "message": "Felicidades te has inscripto correctamente al curso.",
                "enrollment_id": enrollment_id
            },
            status=status.HTTP_201_CREATED
        )


#------------------GET/listEnrollment 
class ListEnrollmentsAPIView(APIView):
    permission_classes = [IsOwnerOrAdmin]
    
    @extend_schema(
        summary="Lista de inscripciones",
        description="Devuelve una lista de las inscripciones a cursos si es admin ve todo, si es profesor solo ve lo referente a sus cursos",
        responses={200: CourseAvailableListSerializer(many=True)}
    )
    def get(self, request):
        user = request.user
        
        # 1. VALIDACIÓN EXPLÍCITA DE ROL
        # Usamos tu función auxiliar get_user_role definida en tu archivo
        role = get_user_role(user)
        
        # AGREGA ESTA LÍNEA Y MIRA LA TERMINAL DE DOCKER
        print(f"DEBUG: El usuario {user.username} fue detectado con rol: {role}")
        
        if role not in ['ADMIN', 'PROFESSOR']:
            return Response(
                {"detail": "Si no es Admin o profesor, no puede visualizar este contenido."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. LÓGICA DE NEGOCIO
        all_enrollments = get_all_enrollments_db()
        is_admin = user.is_staff or user.is_superuser
        
        if is_admin:
            data_to_serialize = all_enrollments
        else:
            data_to_serialize = [
                item for item in all_enrollments 
                if item['professor_name'] == user.username
            ]
        
        # 3. CONEXIÓN CON EL SERIALIZER
        serializer = EnrollmentListSerializer(data_to_serialize, many=True)
        
        # 4. RESPUESTA
        return Response(serializer.data, status=status.HTTP_200_OK)