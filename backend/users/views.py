"""
users/views.py — Versión unificada

Combina:
- Serializers y validaciones OWASP del equipo frontend
- UserProfile + UserConfig con señales (models.py del equipo)
- Login por email
- JWT (SimpleJWT) en lugar de Token DRF
- api_profile con GET/PUT/PATCH
- Paginación en listado de usuarios
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import (
    extend_schema, OpenApiResponse, OpenApiExample, inline_serializer
)

from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    RegisterRequestSerializer,
    RegisterResponseSerializer,
    ProfileUpdateSerializer,
    ProfileUpdateResponseSerializer,
    UserDetailSerializer,
    LogoutResponseSerializer,
)


# ── Helper JWT ────────────────────────────────────────────────────────────────

def _tokens_for_user(user):
    """Genera access + refresh JWT para un usuario."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }


# ── Login ─────────────────────────────────────────────────────────────────────

@extend_schema(
    tags=['auth'],
    summary="Inicio de sesión",
    description="Recibe email y password. Devuelve access + refresh JWT junto con perfil y configuración del usuario.",
    request=LoginRequestSerializer,
    responses={
        200: LoginResponseSerializer,
        400: OpenApiResponse(
            description="Credenciales inválidas o campos vacíos.",
            examples=[
                OpenApiExample('Email vacío',        value={"email": ["El email es un campo obligatorio."]},    response_only=True, status_codes=["400"]),
                OpenApiExample('Password vacío',     value={"password": ["El password es un campo obligatorio."]}, response_only=True, status_codes=["400"]),
                OpenApiExample('Credenciales malas', value={"error": "Credenciales inválidas."},                response_only=True, status_codes=["400"]),
                OpenApiExample('Usuario inactivo',   value={"error": "Este usuario está desactivado."},        response_only=True, status_codes=["400"]),
            ]
        )
    }
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def api_login(request):
    serializer = LoginRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email    = serializer.validated_data['email']
    password = serializer.validated_data['password']

    # Obtener username a partir del email para authenticate()
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=user_obj.username, password=password)

    if user is None:
        return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_400_BAD_REQUEST)
    if not user.is_active:
        return Response({'error': 'Este usuario está desactivado.'}, status=status.HTTP_400_BAD_REQUEST)

    tokens  = _tokens_for_user(user)
    profile = getattr(user, 'profile', None)
    config  = getattr(user, 'config', None)

    return Response({
        'message': 'Login exitoso',
        **tokens,
        'user': {
            'id':         user.id,
            'username':   user.username,
            'email':      user.email,
            'is_staff':   user.is_staff,
            'phone':      profile.phone      if profile else '',
            'avatar_url': profile.avatar_url if profile else '',
            'config': {
                'font_size':      config.font_size      if config else 'MEDIUM',
                'high_contrast':  config.high_contrast  if config else False,
                'voice_guidance': config.voice_guidance if config else False,
            }
        }
    }, status=status.HTTP_200_OK)


# ── Register ──────────────────────────────────────────────────────────────────

@extend_schema(
    tags=['auth'],
    summary="Registro de usuario",
    description="Crea usuario con perfil (phone, avatar) y config de accesibilidad. Devuelve JWT.",
    request=RegisterRequestSerializer,
    responses={
        201: RegisterResponseSerializer,
        400: OpenApiResponse(
            description="Errores de validación.",
            examples=[
                OpenApiExample('Contraseña débil',   value={"password": ["La contraseña debe contener un mínimo de 8 caracteres, una mayúscula y un número."]}, response_only=True, status_codes=["400"]),
                OpenApiExample('No coinciden',        value={"password_confirm": ["Las contraseñas ingresadas no coinciden."]}, response_only=True, status_codes=["400"]),
                OpenApiExample('Email duplicado',     value={"email": ["Este correo electrónico ya se encuentra registrado."]}, response_only=True, status_codes=["400"]),
                OpenApiExample('Username duplicado',  value={"username": ["El nombre de usuario ya está registrado."]}, response_only=True, status_codes=["400"]),
            ]
        )
    }
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def api_register(request):
    serializer = RegisterRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            password=make_password(data['password']),
        )

        # Perfil — creado por señal, solo actualizamos
        profile = user.profile
        profile.phone      = data.get('phone', '')
        profile.avatar_url = data.get('avatar_url', '')
        profile.save()

        # Config — creada por señal, solo actualizamos
        config = user.config
        config.font_size      = data.get('font_size', 'MEDIUM')
        config.high_contrast  = data.get('high_contrast', False)
        config.voice_guidance = data.get('voice_guidance', False)
        config.save()

        tokens = _tokens_for_user(user)

        return Response({
            'message': 'Usuario registrado exitosamente',
            **tokens,
            'user': {
                'id':         user.id,
                'username':   user.username,
                'email':      user.email,
                'phone':      profile.phone,
                'avatar_url': profile.avatar_url,
                'config': {
                    'font_size':      config.font_size,
                    'high_contrast':  config.high_contrast,
                    'voice_guidance': config.voice_guidance,
                }
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'Error al registrar el usuario: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Logout ────────────────────────────────────────────────────────────────────

@extend_schema(
    tags=['auth'],
    summary="Cierre de sesión",
    description="Invalida el refresh token JWT.",
    request=inline_serializer('LogoutRequest', fields={'refresh': serializers.CharField()}),
    responses={200: LogoutResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'error': 'Se requiere el refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        pass
    return Response({'message': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)


# ── Me / Profile ──────────────────────────────────────────────────────────────

@extend_schema(
    methods=['GET'],
    tags=['auth'],
    summary="Obtener perfil del usuario autenticado",
    responses={200: UserDetailSerializer}
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    tags=['auth'],
    summary="Actualizar perfil del usuario autenticado",
    description="Actualiza email, teléfono, avatar y configuración de accesibilidad.",
    request=ProfileUpdateSerializer,
    responses={
        200: ProfileUpdateResponseSerializer,
        400: OpenApiResponse(description="Error en los campos o email duplicado."),
    }
)
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    user    = request.user
    profile = getattr(user, 'profile', None)
    config  = getattr(user, 'config', None)

    if request.method == 'GET':
        return Response({
            'id':         user.id,
            'username':   user.username,
            'email':      user.email,
            'is_staff':   user.is_staff,
            'date_joined': user.date_joined,
            'phone':      profile.phone      if profile else '',
            'avatar_url': profile.avatar_url if profile else '',
            'config': {
                'font_size':      config.font_size      if config else 'MEDIUM',
                'high_contrast':  config.high_contrast  if config else False,
                'voice_guidance': config.voice_guidance if config else False,
            }
        })

    serializer = ProfileUpdateSerializer(data=request.data, partial=(request.method == 'PATCH'))
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Email
    email = data.get('email')
    if email and email != user.email:
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            return Response({'error': 'El correo electrónico ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)
        user.email = email
    user.save()

    # Perfil
    if profile:
        if 'phone'      in data: profile.phone      = data['phone']
        if 'avatar_url' in data: profile.avatar_url = data['avatar_url']
        profile.save()

    # Config
    if config:
        if 'font_size'      in data: config.font_size      = data['font_size']
        if 'high_contrast'  in data: config.high_contrast  = data['high_contrast']
        if 'voice_guidance' in data: config.voice_guidance = data['voice_guidance']
        config.save()

    return Response({
        'message': 'Perfil actualizado exitosamente',
        'user': {
            'id':         user.id,
            'username':   user.username,
            'email':      user.email,
            'phone':      profile.phone      if profile else '',
            'avatar_url': profile.avatar_url if profile else '',
            'config': {
                'font_size':      config.font_size      if config else 'MEDIUM',
                'high_contrast':  config.high_contrast  if config else False,
                'voice_guidance': config.voice_guidance if config else False,
            }
        }
    }, status=status.HTTP_200_OK)


# ── Change Password ───────────────────────────────────────────────────────────

@extend_schema(
    tags=['auth'],
    summary="Cambiar contraseña",
    request=inline_serializer('ChangePasswordRequest', fields={
        'current_password': serializers.CharField(),
        'new_password':     serializers.CharField(),
        'confirm_password': serializers.CharField(),
    }),
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_change_password(request):
    current  = request.data.get('current_password', '')
    new_pass = request.data.get('new_password', '')
    confirm  = request.data.get('confirm_password', '')

    if not request.user.check_password(current):
        return Response({'error': 'La contraseña actual es incorrecta.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(new_pass) < 8 or not any(c.isupper() for c in new_pass) or not any(c.isdigit() for c in new_pass):
        return Response({'error': 'La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número.'}, status=status.HTTP_400_BAD_REQUEST)
    if new_pass != confirm:
        return Response({'error': 'Las contraseñas no coinciden.'}, status=status.HTTP_400_BAD_REQUEST)

    request.user.set_password(new_pass)
    request.user.save()
    return Response({'message': 'Contraseña actualizada correctamente.'})


# ── Users list (paginado) ─────────────────────────────────────────────────────

@extend_schema(
    tags=['auth'],
    summary="Listado de usuarios (paginado)",
    description="Solo staff. Devuelve 10 usuarios por página.",
    responses={
        200: inline_serializer('PaginatedUserList', fields={
            'count':    serializers.IntegerField(),
            'next':     serializers.URLField(allow_null=True),
            'previous': serializers.URLField(allow_null=True),
            'results':  UserDetailSerializer(many=True),
        })
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_users_list(request):
    if not request.user.is_staff:
        return Response({'error': 'Acceso restringido.'}, status=status.HTTP_403_FORBIDDEN)

    users = User.objects.select_related('profile', 'config').all().order_by('id')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    page    = paginator.paginate_queryset(users, request)
    serializer = UserDetailSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)
