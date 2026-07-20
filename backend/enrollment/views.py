from enrollment.signals import trigger_enrollment_email
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status, permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer

from .serializers import CourseAvailableListSerializer, EnrollmentCreateSerializer, EnrollmentListSerializer
from .pagination import StandardResultsSetPagination
from enrollment.permissions import IsOwnerOrAdmin
from .permissions import get_user_role
from .db import get_available_courses, enroll_student_in_course, get_all_enrollments_db
from .db import get_my_enrollments_db
from .serializers import EnrollmentListSerializerStudent


#------------------GET/coursesActive 
#Los 3 roles pueden acceder a ver la lista de courses activos. 
class AvailableCoursesAPIView(APIView):
    
    permission_classes = [IsAuthenticated]

    @extend_schema(
            tags=['enrollment'],
            summary="Lista de cursos disponibles activados",
            description="Devuelve una lista paginada de todos los cursos activos para usuarios autenticados.",
            parameters=[
                OpenApiParameter(
                    name='page', 
                    type=int, 
                    location=OpenApiParameter.QUERY, 
                    required=False, 
                    default=1,
                    description='Número de página a consultar. Por defecto es la página 1'
                )
       ],
        responses={
            200: inline_serializer(
                name='PaginatedCourseList',
                fields={
                    'count': serializers.IntegerField(),
                    'total_pages': serializers.IntegerField(),
                    'next': serializers.URLField(allow_null=True),
                    'previous': serializers.URLField(allow_null=True),
                    'results': CourseAvailableListSerializer(many=True)
                }
            )
        }
    )
    def get(self, request):

        courses = get_available_courses()
    
        paginator = StandardResultsSetPagination()

        page = paginator.paginate_queryset(courses, request, view=self)
        
        if page is not None:
            serializer = CourseAvailableListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        serializer = CourseAvailableListSerializer(courses, many=True)
        return Response({
            'count': len(courses),
            'total_pages': 1,
            'next': None,
            'previous': None,
            'results': serializer.data
        })
        

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

        # Disparamos el correo sin bloquear el retorno
        trigger_enrollment_email(request.user, course_id)

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
        role = get_user_role(user)

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

#---------------Get /lista de cursos particular de cada alumno, solo disponible para el rol student
class MyEnrollmentsListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Cursos particulares del alumno",
        description="Devuelve la lista de cursos en los que el estudiante autenticado está inscrito. Solo disponible para el rol student",
        responses={200: EnrollmentListSerializerStudent(many=True)}
    )
    def get(self, request):
        # 1. Validación de ROL
        try:
            user_role = request.user.profile.role 
        except AttributeError:
            return Response(
                {"detail": "Error: usuario sin perfil de alumno asignado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_role != 'STUDENT':
            return Response(
                {"detail": "Error: solo puedes consultar tus cursos, si tu rol es estudiante."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. Obtener los datos usando la función de base de datos
        my_courses = get_my_enrollments_db(request.user.email)
        
        # 3. Serializar usando el serializador específico
        serializer = EnrollmentListSerializerStudent(my_courses, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    