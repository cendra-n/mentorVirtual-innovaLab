from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample, inline_serializer
from rest_framework import serializers


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Registrar nuevo usuario",
        request=inline_serializer('RegisterRequest', fields={
            'username': serializers.CharField(),
            'email':    serializers.EmailField(),
            'password': serializers.CharField(),
        }),
        examples=[OpenApiExample('Ejemplo', value={
            'username': 'juanperez',
            'email':    'juan@email.com',
            'password': 'mipass1234',
        })],
    )
    def post(self, request):
        username = request.data.get('username', '').strip()
        email    = request.data.get('email', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'error': 'username y password son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(password) < 8:
            return Response(
                {'error': 'La contraseña debe tener al menos 8 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'El nombre de usuario ya está en uso.'},
                status=status.HTTP_409_CONFLICT,
            )
        if email and User.objects.filter(email=email).exists():
            return Response(
                {'error': 'El email ya está registrado.'},
                status=status.HTTP_409_CONFLICT,
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return Response(
            {
                'message': '¡Cuenta creada exitosamente!',
                'user_id': user.id,
                'username': user.username,
                **_tokens_for_user(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login — obtener tokens JWT",
        request=inline_serializer('LoginRequest', fields={
            'username': serializers.CharField(),
            'password': serializers.CharField(),
        }),
        examples=[OpenApiExample('Usuario demo', value={
            'username': 'demo',
            'password': 'demo1234',
        })],
    )
    def post(self, request):
        from django.contrib.auth import authenticate

        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'error': 'Credenciales inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response({
            'user_id':  user.id,
            'username': user.username,
            **_tokens_for_user(user),
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Logout — invalidar refresh token",
        request=inline_serializer('LogoutRequest', fields={
            'refresh': serializers.CharField(),
        }),
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Se requiere el refresh token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass
        return Response({'message': 'Sesión cerrada correctamente.'})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Cambiar contraseña del usuario autenticado",
        request=inline_serializer('ChangePasswordRequest', fields={
            'current_password':  serializers.CharField(),
            'new_password':      serializers.CharField(),
            'confirm_password':  serializers.CharField(),
        }),
    )
    def post(self, request):
        current  = request.data.get('current_password', '')
        new_pass = request.data.get('new_password', '')
        confirm  = request.data.get('confirm_password', '')

        if not request.user.check_password(current):
            return Response(
                {'error': 'La contraseña actual es incorrecta.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(new_pass) < 8:
            return Response(
                {'error': 'La nueva contraseña debe tener al menos 8 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_pass != confirm:
            return Response(
                {'error': 'Las contraseñas no coinciden.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.set_password(new_pass)
        request.user.save()
        return Response({'message': 'Contraseña actualizada correctamente.'})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Datos del usuario autenticado")
    def get(self, request):
        u = request.user
        return Response({
            'user_id':    u.id,
            'username':   u.username,
            'email':      u.email,
            'first_name': u.first_name,
            'last_name':  u.last_name,
            'is_staff':   u.is_staff,
            'date_joined': u.date_joined,
        })
