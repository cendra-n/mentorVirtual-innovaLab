from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import UserProfile, UserConfig


class UserConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConfig
        fields = ['font_size', 'high_contrast', 'voice_guidance']


class UserDetailSerializer(serializers.ModelSerializer):
    phone      = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    role       = serializers.SerializerMethodField()
    config     = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'avatar_url', 'config']

    def get_phone(self, obj):
        return getattr(obj.profile, 'phone', '') if hasattr(obj, 'profile') else ''

    def get_avatar_url(self, obj):
        return getattr(obj.profile, 'avatar_url', '') if hasattr(obj, 'profile') else ''

    def get_role(self, obj):
        return getattr(obj.profile, 'role', 'STUDENT') if hasattr(obj, 'profile') else 'STUDENT'

    def get_config(self, obj):
        if not hasattr(obj, 'config'):
            return {'font_size': 'MEDIUM', 'high_contrast': False, 'voice_guidance': False}
        return UserConfigSerializer(obj.config).data


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'El email es un campo obligatorio.',
            'blank':    'El email es un campo obligatorio.',
            'invalid':  'Introduzca una dirección de correo electrónico válida.'
        },
        help_text="Dirección de correo electrónico asociada a la cuenta."
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            'required': 'El password es un campo obligatorio.',
            'blank':    'El password es un campo obligatorio.'
        },
        help_text="Contraseña de la cuenta."
    )


class LoginResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    refresh = serializers.CharField(help_text="Refresh token JWT.")
    access  = serializers.CharField(help_text="Access token JWT (Bearer).")
    user    = UserDetailSerializer()


class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        error_messages={
            'required': 'El username es un campo obligatorio.',
            'blank':    'El username es un campo obligatorio.'
        },
        help_text="Nombre de usuario único."
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'El email es un campo obligatorio.',
            'blank':    'El email es un campo obligatorio.',
            'invalid':  'Introduzca una dirección de correo electrónico válida.'
        },
        help_text="Email único con formato válido."
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            'required': 'El password es un campo obligatorio.',
            'blank':    'El password es un campo obligatorio.'
        },
        help_text="Mínimo 8 caracteres, una mayúscula, un número y un carácter especial."
    )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            'required': 'El password_confirm es un campo obligatorio.',
            'blank':    'El password_confirm es un campo obligatorio.'
        },
        help_text="Debe coincidir con password."
    )

    phone_regex = RegexValidator(
        regex=r'^\+?\d{7,15}$',
        message="Formato válido: +541123456789 o 1123456789 (7 a 15 dígitos)."
    )
    phone = serializers.CharField(
        validators=[phone_regex], required=False, allow_blank=True, default='',
        help_text="Teléfono de contacto (opcional)."
    )
    avatar_url = serializers.CharField(
        required=False, allow_blank=True, default='',
        help_text="URL de avatar (opcional)."
    )
    font_size = serializers.ChoiceField(
        choices=['SMALL', 'MEDIUM', 'LARGE'], required=False, default='MEDIUM',
        error_messages={'invalid_choice': 'El tamaño de fuente seleccionado no es válido. Las opciones permitidas son: SMALL, MEDIUM, LARGE.'},
        help_text="Tamaño de tipografía de accesibilidad (default: MEDIUM)."
    )
    high_contrast = serializers.BooleanField(
        required=False, default=False,
        help_text="Activar contraste elevado (default: false)."
    )
    voice_guidance = serializers.BooleanField(
        required=False, default=False,
        help_text="Activar guía por voz (default: false)."
    )

    def validate(self, data):
        password         = data.get('password', '')
        password_confirm = data.get('password_confirm', '')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': ['Las contraseñas ingresadas no coinciden.']
            })

        if (len(password) < 8 or
                not any(c.isupper() for c in password) or
                not any(c.isdigit() for c in password) or
                not any(not c.isalnum() for c in password)):
            raise serializers.ValidationError({
                'password': ['La contraseña debe contener mínimo 8 caracteres, una mayúscula, un número y un carácter especial.']
            })

        email = data.get('email', '').strip().lower()
        data['email'] = email
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': ['Este correo electrónico ya se encuentra registrado.']
            })

        username = data.get('username', '').strip().lower()
        data['username'] = username
        if username:
            if ' ' in username:
                raise serializers.ValidationError({
                    'username': ['El nombre de usuario no puede contener espacios.']
                })
            if username.isdigit():
                raise serializers.ValidationError({
                    'username': ['El nombre de usuario no puede estar compuesto únicamente por números.']
                })
            import re
            if not re.match(r'^[\w.@+-]+$', username):
                raise serializers.ValidationError({
                    'username': ['El nombre de usuario contiene caracteres no válidos.']
                })
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError({
                    'username': ['El nombre de usuario ya está registrado.']
                })

        return data


class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    refresh = serializers.CharField(help_text="Refresh token JWT.")
    access  = serializers.CharField(help_text="Access token JWT (Bearer).")
    user    = UserDetailSerializer()


class ProfileUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=False,
        help_text="Nuevo email (debe ser único)."
    )
    phone = serializers.CharField(
        required=False, allow_blank=True,
        help_text="Nuevo teléfono de contacto."
    )
    avatar_url = serializers.CharField(
        required=False, allow_blank=True,
        help_text="Nueva URL de avatar."
    )
    font_size = serializers.ChoiceField(
        choices=['SMALL', 'MEDIUM', 'LARGE'], required=False,
        error_messages={'invalid_choice': 'El tamaño de fuente seleccionado no es válido. Las opciones permitidas son: SMALL, MEDIUM, LARGE.'},
        help_text="Nuevo tamaño de tipografía."
    )
    high_contrast = serializers.BooleanField(
        required=False,
        help_text="Nueva preferencia de alto contraste."
    )
    voice_guidance = serializers.BooleanField(
        required=False,
        help_text="Nueva preferencia de guía por voz."
    )

    def validate_email(self, value):
        request = self.context.get('request')
        value   = value.lower()
        if request and request.user:
            if User.objects.filter(email=value).exclude(pk=request.user.pk).exists():
                raise serializers.ValidationError(
                    "Este correo electrónico ya se encuentra registrado por otro usuario."
                )
        return value


class ProfileUpdateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user    = UserDetailSerializer()


class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField(
        help_text="Confirmación del cierre de sesión."
    )
