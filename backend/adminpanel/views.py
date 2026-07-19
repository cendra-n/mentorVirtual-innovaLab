import re
import logging # <-- IMPORTANTE: Módulo para registrar los errores en el servidor
from django.contrib.auth.models import User
from django.db import connection, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from users.models import UserProfile, ProfessorProfile
from users.serializers import AdminCreateProfessorSerializer
from users.pagination import CustomPagination

# Configuración del logger estándar para esta vista
logger = logging.getLogger(__name__) 

class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')

        paginator = CustomPagination()
        page = paginator.paginate_queryset(users, request, view=self)

        data = []
        for u in page:
            role = 'STUDENT'
            if hasattr(u, 'profile'):
                role = u.profile.role
            data.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'is_active': u.is_active,
                'is_staff': u.is_staff,
                'date_joined': u.date_joined,
                'role': role,
                'avatar_url': u.profile.avatar_url if hasattr(u, 'profile') else ''
            })
        return paginator.get_paginated_response(data)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            u = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)
        
        role = 'STUDENT'
        if hasattr(u, 'profile'):
            role = u.profile.role
        return Response({
            'id': u.id, 'username': u.username, 'email': u.email,
            'is_active': u.is_active, 'is_staff': u.is_staff,
            'date_joined': u.date_joined,
            'role': role
        })

    def patch(self, request, user_id):
        try:
            u = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)

        if 'is_active' in request.data:
            u.is_active = request.data['is_active']
        if 'is_staff' in request.data:
            u.is_staff = request.data['is_staff']
        
        if 'role' in request.data:
            new_role = request.data['role']
            if new_role in ['STUDENT', 'PROFESSOR', 'ADMIN']:
                if hasattr(u, 'profile'):
                    u.profile.role = new_role
                    u.profile.save()
                else:
                    UserProfile.objects.create(user=u, role=new_role)

                # Si cambia a PROFESSOR, nos aseguramos de crear el legajo ProfessorProfile si no existe
                if new_role == 'PROFESSOR':
                    if not hasattr(u, 'professor_profile'):
                        dni_ficticio = f"{u.id:08d}"[-8:]
                        while ProfessorProfile.objects.filter(dni=dni_ficticio).exists():
                            import random
                            dni_ficticio = f"{random.randint(10000000, 99999999)}"
                        
                        ProfessorProfile.objects.create(
                            user=u,
                            dni=dni_ficticio,
                            address="Dirección provisional",
                            birth_date="1990-01-01"
                        )
        
        u.save()
        return Response({'message': 'Usuario actualizado.'})


class AdminSetPasswordView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            u = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)

        password = request.data.get('password', '')
        if len(password) < 8:
            return Response(
                {'error': 'La contraseña debe tener al menos 8 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        u.set_password(password)   # hashea correctamente
        u.save()
        return Response({'message': f'Contraseña de {u.username} actualizada correctamente.'})


class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        with connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM auth_user")
            total_users = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM goals")
            total_goals = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM user_progress")
            total_steps_completed = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM video_views")
            total_video_views = cur.fetchone()[0]

        return Response({
            'total_users':           total_users,
            'total_goals':           total_goals,
            'total_steps_completed': total_steps_completed,
            'total_video_views':     total_video_views,
        })


# ── NUEVO ENDPOINT DIRECTO PARA CREAR PROFESORES (Solo activo desde admin y pensando en datos para requerimientos laborales) ──

class AdminCreateProfessorView(APIView):
    """
    Endpoint estratégico que permite al administrador registrar un profesor desde el frontend...
    """
    permission_classes = [IsAdminUser]
    # línea para que Swagger reconozca los campos:
    serializer_class = AdminCreateProfessorSerializer

    def post(self, request):
        # 1. Pasamos los datos al serializador para ejecutar las validaciones de negocio básicas y de tipos
        serializer = AdminCreateProfessorSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 2. Extraemos los datos validados y limpios del serializador
        data = serializer.validated_data

        # IMPORTANTE: Preservamos los espacios en el username (ya validados por el serializer)
        username = data.get('username').strip() 
        email = data.get('email').strip().lower()
        password = data.get('password')
        dni = data.get('dni').strip()
        address = data.get('address')
        birth_date = data.get('birth_date') # Obtenido de forma segura del serializer

        # 3. Espejo de validaciones estrictas del password de la app
        if (len(password) < 8 or
                not any(c.isupper() for c in password) or
                not any(c.isdigit() for c in password) or
                not any(not c.isalnum() for c in password)):
            return Response(
                {'error': 'La contraseña debe contener mínimo 8 caracteres, una mayúscula, un número y un carácter especial.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # [CORRECCIÓN] Se eliminan las validaciones viejas de username que prohibían los espacios

        # Validación estricta del DNI (8 números)
        if not re.match(r'^\d{8}$', dni):
            return Response({'error': 'El DNI ministerial debe contener exactamente 8 dígitos numéricos.'}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Verificaciones de unicidad en Base de Datos usando __iexact para ignorar mayúsculas/minúsculas
        if User.objects.filter(username__iexact=username).exists():
            return Response({'error': 'El nombre de usuario ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Este correo electrónico ya se encuentra registrado.'}, status=status.HTTP_400_BAD_REQUEST)
        if ProfessorProfile.objects.filter(dni=dni).exists():
            return Response({'error': 'Ya existe un profesor registrado con este DNI.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Transacción atómica integral para prevenir registros huérfanos
            with transaction.atomic():
                # 5. Crear el usuario base hasheando la contraseña de forma segura
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                # 6. Forzar la reconfiguración del Perfil a modo PROFESSOR
                profile = user.profile
                profile.role = 'PROFESSOR'
                profile.phone = data.get('phone', '')
                profile.avatar_url = data.get('avatar_url', '')
                profile.save()

                # 7. Sanear la base de datos eliminando el perfil analítico de estudiante generado por la señal
                if hasattr(user, 'student_analytics'):
                    user.student_analytics.delete()

                # 8. Crear el legajo contractual del profesor (incluyendo la fecha de nacimiento)
                ProfessorProfile.objects.create(
                    user=user,
                    dni=dni,
                    address=address,
                    birth_date=birth_date,
                    title_degree=data.get('title_degree', '')
                )

            # Reemplazamos el punto interno por un espacio estético para el cliente
            username_friendly = user.username.replace('.', ' ')
            return Response({
                'message': f"Profesor '{username_friendly}' registrado de manera directa con éxito.",
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Enzo Fix: Logueamos la falla transaccional real y protegemos al cliente
            logger.error(f"Fallo interno en la transacción de creación de profesor: {str(e)}", exc_info=True)
            return Response(
                {'error': "Ha ocurrido un error interno en el servidor al procesar la transacción de la base de datos."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )