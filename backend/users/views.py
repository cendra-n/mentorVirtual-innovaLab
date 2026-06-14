from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter, inline_serializer
from rest_framework.pagination import PageNumberPagination #para implementar paginación
from .pagination import CustomPagination
from .models import UserProfile 
from rest_framework_simplejwt.tokens import RefreshToken  # Motor para generar JWT
from rest_framework_simplejwt.authentication import JWTAuthentication


from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    RegisterRequestSerializer,
    RegisterResponseSerializer,
    ProfileUpdateSerializer,
    ProfileUpdateResponseSerializer,
    UserDetailSerializer,
    LogoutResponseSerializer
)

@extend_schema(
    summary="Inicio de sesión de usuario",
    description="Recibe credenciales de usuario (email y password), las valida y genera/retorna un Token de Django REST Framework junto con los datos del perfil y configuración del usuario.",
    request=LoginRequestSerializer,
    responses={
        200: LoginResponseSerializer,
        400: OpenApiResponse(
            description="Error de validación (campos vacíos, formato inválido) o credenciales incorrectas.",
            examples=[
                OpenApiExample(
                    name="Campo email vacío",
                    value={"email": ["El email es un campo obligatorio."]},
                    response_only=True,
                    status_codes=["400"]
                ),
                OpenApiExample(
                    name="Campo password vacío",
                    value={"password": ["El password es un campo obligatorio."]},
                    response_only=True,
                    status_codes=["400"]
                ),
                OpenApiExample(
                    name="Credenciales incorrectas",
                    value={"error": "Credenciales inválidas."},
                    response_only=True,
                    status_codes=["400"]
                ),
                OpenApiExample(
                    name="Usuario desactivado",
                    value={"error": "Este usuario está desactivado."},
                    response_only=True,
                    status_codes=["400"]
                )
            ]
        )
    }
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny]) 
def api_login(request):
    """
    Vista de inicio de sesión.
    Recibe email y password, valida a través del serializer y retorna un Token de DRF
    junto con los datos del perfil y configuración del usuario.
    """
    serializer = LoginRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data.get('email')
    password = serializer.validated_data.get('password')

    try:
        user = UserProfile.objects.get(email=email)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Validamos la contraseña cifrada
    if user.check_password(password):
        if user.is_active:
            login(request, user)
            
            # GENERACIÓN DE TOKEN JWT (MIGRACIÓN COMPLETADA)
            refresh = RefreshToken.for_user(user)
            
            # Recuperamos las preferencias directamente del usuario y su config asociada
            font_size = user.config.font_size if hasattr(user, 'config') else 'MEDIUM'
            high_contrast = user.config.high_contrast if hasattr(user, 'config') else False
            voice_guidance = user.config.voice_guidance if hasattr(user, 'config') else False
            
            return Response({
                'message': 'Login exitoso',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,  # Le mandamos el rol al Front-end
                    'phone': user.phone,
                    'avatar_url': user.avatar_url,
                    'config': {
                        'font_size': font_size,
                        'high_contrast': high_contrast,
                        'voice_guidance': voice_guidance
                    }
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Este usuario está desactivado.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    summary="Registro de usuario",
    description="Recibe username, password, password_confirm, email y opcionalmente teléfono, avatar_url y opciones de accesibilidad. Crea el usuario y sus relaciones (UserProfile, UserConfig), y retorna un Token activo.",
    request=RegisterRequestSerializer,
    responses={
        201: RegisterResponseSerializer,
        400: OpenApiResponse(
            description="Errores de validación en los campos enviados (vacíos, contraseñas no coincidentes, contraseña débil, email duplicado o nombre de usuario existente).",
            examples=[
                OpenApiExample(
                    name="Contraseña débil (OWASP)",
                    value={"password": ["La contraseña debe contener un mínimo de 8 caracteres, una mayúscula y un número."]},
                    response_only=True,
                    status_codes=["400"]
                ),
                OpenApiExample(
                    name="Contraseñas no coinciden",
                    value={"password_confirm": ["Las contraseñas ingresadas no coinciden."]},
                    response_only=True,
                    status_codes=["400"]
                ),
                OpenApiExample(
                    name="Email duplicado",
                    value={"email": ["Este correo electrónico ya se encuentra registrado."]},
                    response_only=True,
                    status_codes=["400"]
                ),
                OpenApiExample(
                    name="Nombre de usuario duplicado",
                    value={"username": ["El nombre de usuario ya está registrado."]},
                    response_only=True,
                    status_codes=["400"]
                ),
                OpenApiExample(
                    name="Campo requerido vacío",
                    value={"username": ["El username es un campo obligatorio."]},
                    response_only=True,
                    status_codes=["400"]
                )
            ]
        ),
        500: OpenApiResponse(description="Error al registrar el usuario.")
    }
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def api_register(request):
    """
    Vista de registro de usuario.
    Recibe username, password, password_confirm, email y opcionalmente teléfono, avatar_url y opciones de accesibilidad.
    Valida la petición a través del serializer y crea el usuario con su perfil y configuración. Retorna un Token de DRF activo.
    """
    serializer = RegisterRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    data = serializer.validated_data       
    try:
        # Extraemos los datos validados del serializador
        data = serializer.validated_data
        
        user = UserProfile.objects.create(
            username=data.get('username'),
            email=data.get('email'),
            password=make_password(data.get('password')),  # Hasheamos la contraseña por seguridad
            phone=data.get('phone', ''),
            avatar_url=data.get('avatar_url', ''),
            role='STUDENT'  # Asignamos el rol ALUMNO por requerimiento directo
        )
        
        config = user.config
        config.font_size = data.get('font_size', 'MEDIUM')
        config.high_contrast = data.get('high_contrast', False)
        config.voice_guidance = data.get('voice_guidance', False)
        config.save()
        
        # Generamos los tokens JWT para que el usuario quede logueado automáticamente al crearse
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'phone': user.phone,
                'avatar_url': user.avatar_url,
                'config': {
                    'font_size': config.font_size,
                    'high_contrast': config.high_contrast,
                    'voice_guidance': config.voice_guidance
                }
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Error al registrar el usuario en el sistema: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    summary="Cierre de sesión",
    description="Requiere token de autenticación en cabecera y elimina dicho token de la base de datos para invalidar futuros accesos del mismo.",
    responses={
        200: LogoutResponseSerializer,
        500: OpenApiResponse(description="Error al cerrar sesión.")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """
    Vista de cierre de sesión.
    Requiere token de autenticación en cabecera y elimina dicho token de la base de datos
    para invalidar futuros accesos del mismo.
    """
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()  # Invalida el token permanentemente
        return Response({'message': 'Sesión cerrada exitosamente.'}, status=status.HTTP_200_OK)
    except Exception as e:
        # Fallback por si no tienen activada la app de blacklist en settings, devuelve un 200 informativo
        return Response({'message': 'Sesión cerrada localmente.'}, status=status.HTTP_200_OK)


@extend_schema(
    methods=['GET'],
    summary="Obtener perfil de usuario logueado",
    description="Obtiene los datos detallados del usuario logueado, incluyendo su perfil y configuración.",
    responses={200: UserDetailSerializer}
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    summary="Actualizar perfil de usuario logueado",
    description="Actualiza el perfil y configuración del usuario logueado (campos como email, teléfono, avatar o configuraciones de accesibilidad).",
    request=ProfileUpdateSerializer,
    responses={
        200: ProfileUpdateResponseSerializer,
        400: OpenApiResponse(description="Error en los campos enviados o conflicto de correo electrónico.")
    }
)
@api_view(['GET', 'PUT', 'PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_profile(request):
    """
    Vista para ver o actualizar el perfil del usuario autenticado.
    Soporta GET, PUT y PATCH. Requiere autenticación por Token.
    """
    user = request.user
    config = user.config

    if request.method == 'GET':
        # Nota: Asegurar que UserDetailSerializer apunte directo a campos de UserProfile
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        # Validación parcial o completa según el método
        serializer = ProfileUpdateSerializer(data=request.data, partial=(request.method == 'PATCH'))
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Actualizar email del usuario si se proporciona
        email = data.get('email')
        if email is not None:
            if email != user.email and UserProfile.objects.filter(email=email).exclude(id=user.id).exists():
                return Response({'error': 'El correo electrónico ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = email
        user.save()

        # Actualizar datos de perfil
        if data.get('phone') is not None:
            user.phone = data.get('phone')
        if data.get('avatar_url') is not None:
            user.avatar_url = data.get('avatar_url')
        user.save()

        if data.get('font_size') is not None:
            config.font_size = data.get('font_size')
        if data.get('high_contrast') is not None:
            config.high_contrast = data.get('high_contrast')
        if data.get('voice_guidance') is not None:
            config.voice_guidance = data.get('voice_guidance')
        config.save()

        # Respuesta con el perfil de usuario actualizado
        response_serializer = UserDetailSerializer(user)
        return Response({
            'message': 'Perfil actualizado exitosamente',
            'user': response_serializer.data
        }, status=status.HTTP_200_OK)


#metodo de paginacion con boton sin validaciones extra
# @extend_schema(
#     summary="Listado de todos los usuarios",
#     description="Retorna una lista paginada de todos los usuarios registrados, incluyendo su perfil y su configuración de accesibilidad. Devuelve 10 registros por página",
#     #  SE AGREGA EL PARÁMETRO PARA LA INTERFAZ DE SWAGGER 
#     parameters=[
#         OpenApiParameter(
#             name='page',
#             type=int,
#             location=OpenApiParameter.QUERY,
#             required=False,
#             description='Número de página a consultar para el listado de usuarios.'
#         )
#     ],
#     responses={
#         200: inline_serializer(
#             name='PaginatedUserList',
#             fields={
#                 'count': serializers.IntegerField(help_text='Total number of users'),
#                 'next': serializers.URLField(allow_null=True, help_text='URL of the next page of users'),
#                 'previous': serializers.URLField(allow_null=True, help_text='URL of the previous page of users'),
#                 'results': UserDetailSerializer(many=True)
#             }
#         )
#     }
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def api_users_list(request):
#     """
#     Vista que devuelve el listado de todos los usuarios registrados con paginación.
#     Requiere autenticación por Token.
#     """
#     # Traemos la query optimizada de la base de datos
#     users = User.objects.select_related('profile', 'config').all().order_by('id')
    
#     # Instanciamos y configuramos el paginador a mano
#     paginator = PageNumberPagination()
#     paginator.page_size = 10  # Podés cambiar el 10 por el tamaño de página que prefieras
    
#     #  Paginamos el QuerySet pasando el request
#     paginated_users = paginator.paginate_queryset(users, request)
    
#     # Serializamos únicamente los datos de la página actual
#     serializer = UserDetailSerializer(paginated_users, many=True)
    
#     # Retornamos la respuesta con la estructura nativa de paginación de DRF (count, next, previous, results)
#     return paginator.get_paginated_response(serializer.data)



@extend_schema(
    summary="Listado de todos los usuarios",
    description="Retorna una lista paginada de todos los usuarios registrados, incluyendo su perfil y su configuración de accesibilidad. Devuelve 10 registros por página",
    parameters=[
        OpenApiParameter(
            name='page',
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            default=1,
            description='Ingrese el número de página. Si ingresa un número mayor al total de páginas disponibles, el sistema retornará un error indicando el límite real.'
        )
    ],
    responses={
        200: inline_serializer(
            name='PaginatedUserListWithTotal',
            fields={
                'count': serializers.IntegerField(help_text='Total number of users'),
                'total_pages': serializers.IntegerField(help_text='Total number of pages available'), # Documentado en Swagger
                'next': serializers.URLField(allow_null=True, help_text='URL of the next page of users'),
                'previous': serializers.URLField(allow_null=True, help_text='URL of the previous page of users'),
                'results': UserDetailSerializer(many=True)
            }
        ),
        404: inline_serializer(
            name='PaginationErrorResponse',
            fields={
                'detail': serializers.CharField(help_text='Mensaje de error cuando la página está vacía')
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_users_list(request):
    """
    Vista que devuelve el listado de todos los usuarios registrados con paginación.
    Requiere autenticación por Token.
    """
    # Traemos la query optimizada de la base de datos
    users = UserProfile.objects.select_related('config').all().order_by('id')
    
    # Reemplazamos el paginador genérico por tu CustomPagination
    paginator = CustomPagination()
    
    # Paginamos el QuerySet pasando el request (aquí se ejecutará el try/except personalizado)
    paginated_users = paginator.paginate_queryset(users, request)
    
    # Serializamos únicamente los datos de la página actual
    serializer = UserDetailSerializer(paginated_users, many=True)
    
    # Retornamos la respuesta con la estructura enriquecida (count, total_pages, next, previous, results)
    return paginator.get_paginated_response(serializer.data)