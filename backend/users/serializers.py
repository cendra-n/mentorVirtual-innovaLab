from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import UserProfile, UserConfig, StudentProfile, EventTypes, UserActivityLog, Country, Province, Locality, Nationality
import re
from datetime import date


class NationalitySerializer(serializers.Serializer):
    nationality_id = serializers.IntegerField()
    nationality_name = serializers.CharField()
    class Meta:
        fields = ['nationality_id', 'nationality_name']

class CountrySerializer(serializers.Serializer):
    country_id = serializers.IntegerField()
    country_name = serializers.CharField()

    class Meta:
        fields = ['country_id', 'country_name']

class ProvinceSerializer(serializers.Serializer):
    province_id = serializers.IntegerField()
    province_name = serializers.CharField()
    country = CountrySerializer()

    class Meta:
        fields = ['province_id', 'province_name', 'country']

class ProvinceSearchSerializer(serializers.Serializer):
    province_name = serializers.CharField(
        max_length=100,
        help_text="Escribe el nombre de la provincia a buscar (ej: Mendoza, Córdoba, Neuquén)"
        )

class LocalitySerializer(serializers.Serializer):
    locality_id = serializers.IntegerField()
    locality_name = serializers.CharField()
    province = ProvinceSerializer()

    class Meta:
        fields = ['locality_id', 'locality_name', 'province']


class UserConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConfig
        fields = ['font_size', 'high_contrast', 'voice_guidance']


class UserDetailSerializer(serializers.ModelSerializer):
    phone      = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    role       = serializers.SerializerMethodField()
    config     = serializers.SerializerMethodField()
    session_status = serializers.SerializerMethodField()
    country_residence  = serializers.SerializerMethodField()
    province_residence = serializers.SerializerMethodField()
    locality_residence = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            'id', 'username', 'email', 'role',
            'phone', 'avatar_url', 'config', 'session_status',
            'country_residence', 'province_residence', 'locality_residence'
        ]

    def get_country_residence(self, obj):
        if hasattr(obj, 'profile') and obj.profile.country_residence:
            return CountrySerializer(obj.profile.country_residence).data
        return None

    def get_province_residence(self, obj):
        if hasattr(obj, 'profile') and obj.profile.province_residence:
            return ProvinceSerializer(obj.profile.province_residence).data
        return None

    def get_locality_residence(self, obj):
        if hasattr(obj, 'profile') and obj.profile.locality_residence:
            return LocalitySerializer(obj.profile.locality_residence).data
        return None

    def get_session_status(self, obj):
        return getattr(obj.profile, 'session_status', 'OFFLINE') if hasattr(obj, 'profile') else 'OFFLINE'

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
    
    #Esto lo que hace es analizar los usuarios y los que tengan rol profesor, estan asi en la db : maria.lopez
    #Con esta función lo que hacemos es que ponga un espacio y saque ese punto a nivel visual desde swagger
    #Pero en la db no hay cambios queda maria.lopez , igualmente el usuario agregar nombre y apellido separado
    #Y en la BD se guarda con el punto 
    def to_representation(self, instance):
        """
        Filtro puramente estético de salida JSON. 
        Reemplaza el punto por espacio SOLAMENTE si el rol es de profesor.
        """
        representation = super().to_representation(instance)
        user_role = representation.get('role')
        
        if user_role == 'PROFESSOR' and 'username' in representation and representation['username']:
            representation['username'] = representation['username'].replace('.', ' ')
            
        return representation


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
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), required=False, allow_null=True,
        help_text="ID del país de residencia (opcional, ver GET /api/auth/geo/countries/)."
    )
    province = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(), required=False, allow_null=True,
        help_text="ID de la provincia de residencia (opcional, ver GET /api/auth/geo/provinces/list?country=<id>)."
    )
    locality = serializers.PrimaryKeyRelatedField(
        queryset=Locality.objects.all(), required=False, allow_null=True,
        help_text="ID de la localidad de residencia (opcional, ver GET /api/auth/geo/localities/?province=<id>)."
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

        # Coherencia jerárquica de geo (opcional): si mandan más de un nivel,
        # tienen que encajar entre sí. Mismo criterio que ProfileUpdateSerializer.
        country  = data.get('country')
        province = data.get('province')
        locality = data.get('locality')
        if province and country and province.country_id != country.country_id:
            raise serializers.ValidationError({
                'province': [f'La provincia seleccionada no pertenece a {country.country_name}.']
            })
        if locality and province and locality.province_id != province.province_id:
            raise serializers.ValidationError({
                'locality': [f'La localidad seleccionada no pertenece a {province.province_name}.']
            })

        return data


class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    refresh = serializers.CharField(help_text="Refresh token JWT.")
    access  = serializers.CharField(help_text="Access token JWT (Bearer).")
    user    = UserDetailSerializer()


class ProfileUpdateSerializer(serializers.Serializer):
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), required=False, allow_null=True,
        help_text="ID del país de residencia (ver GET /api/auth/geo/countries/)."
    )
    province = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(), required=False, allow_null=True,
        help_text="ID de la provincia de residencia (ver GET /api/auth/geo/provinces/list?country=<id>)."
    )
    locality = serializers.PrimaryKeyRelatedField(
        queryset=Locality.objects.all(), required=False, allow_null=True,
        help_text="ID de la localidad de residencia."
    )
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

    def validate(self, data):
        country  = data.get('country')
        province = data.get('province')
        locality = data.get('locality')

        if province and country and province.country_id != country.country_id:
            raise serializers.ValidationError({
                'province': f'La provincia seleccionada no pertenece a {country.country_name}.'
            })
        if locality and province and locality.province_id != province.province_id:
            raise serializers.ValidationError({
                'locality': f'La localidad seleccionada no pertenece a {province.province_name}.'
            })
        return data


class ProfileUpdateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user    = UserDetailSerializer()


class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField(
        help_text="Confirmación del cierre de sesión."
    )


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        # Se excluye el 'user' porque ya viene del contexto del token (request.user)
        exclude = ['user']
        extra_kwargs = {
            'birth_date': {
                'label': 'Fecha de nacimiento',
                'help_text': 'Fecha de nacimiento en formato YYYY-MM-DD.',
                'required': False
            },
            'education_level': {
                'label': 'Nivel Educativo',
                'help_text': 'Nivel educativo alcanzado (ej: primario_completo, secundario_completo).',
                'required': False
            },
            'employment_status': {
                'label': 'Estado laboral',
                'help_text': 'Situación laboral actual (activo, desempleado).',
                'required': False
            },
            'user_interests': {
                'label': 'Intereses',
                'help_text': 'Lista de intereses como arreglo de strings, ej: ["Programación", "Diseño"].',
                'required': False
            },
            'user_gender': {
                'label': 'Género',
                'help_text': 'Género (M, F, NB, ND).',
                'required': False
            },
            'primary_objective': {
                'label': 'Objetivo principal',
                'help_text': 'Motivación principal para usar la app (empleo, personal, estudios, hobby).',
                'required': False
            },
            'time_availability': {
                'label': 'Disponibilidad de tiempo',
                'help_text': 'Tiempo estimado disponible semanalmente (baja, media, alta).',
                'required': False
            },
            'time_zone': {
                'label': 'Zona horaria',
            },
            'entry_frequency': {
                'read_only': True,
                'min_value': 0,
                'max_value': 10000
            },
            'current_streak_days': {
                'read_only': True,
                'min_value': 0,
                'max_value': 3650
            },
            'max_streak_days': {
                'read_only': True,
                'min_value': 0,
                'max_value': 3650
            },
            'app_time_min': {
                'read_only': True,
                'min_value': 0.0
            },
            'mentor_interaction_time_min': {
                'read_only': True,
                'min_value': 0.0
            },
            'watched_videos_count': {
                'read_only': True,
                'min_value': 0
            },
            'youtube_api_time_min': {
                'read_only': True,
                'min_value': 0.0
            },
            'completed_challenges': {
                'read_only': True,
                'min_value': 0
            },
        }

#-----------professor--------------------------------------------
class AdminCreateProfessorSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True, 
        help_text="Nombre y apellido del profesor separado por un espacio (Ej: 'Juan Perez')."
    )
    email = serializers.EmailField(
        required=True, 
        help_text="Dirección de correo electrónico única."
    )
    password = serializers.CharField(
        required=True, 
        write_only=True, 
        help_text="Mínimo 8 caracteres, una mayúscula, un número y un carácter especial."
    )
    
    birth_date = serializers.DateField(
        required=True,
        input_formats=['%Y-%m-%d'],
        help_text="Fecha de nacimiento del profesor (Formato YYYY-MM-DD). Debe tener entre 18 y 65 años."
    )
    dni = serializers.CharField(
        required=True, 
        max_length=8, 
        min_length=8, 
        help_text="DNI de exactamente 8 dígitos."
    )
    address = serializers.CharField(
        required=True, 
        help_text="Dirección residencial del profesor."
    )
    phone = serializers.CharField(required=False, allow_blank=True, default='')
    avatar_url = serializers.CharField(required=False, allow_blank=True, default='')
    title_degree = serializers.CharField(required=False, allow_blank=True, default='', help_text="Título (Opcional).")

    def validate_username(self, value):
        """
        Validación de negocio estricta: El username debe ser 'Nombre Apellido' real.
        - Debe contener obligatoriamente letras y espacios (no se permiten números ni símbolos).
        - Debe incluir al menos un espacio intermedio para separar nombre de apellido.
        - Internamente se normaliza reemplazando espacios por puntos para Django.
        """
        username = value.strip()

        # 1. Verificar que tenga al menos un espacio intermedio
        if ' ' not in username:
            raise serializers.ValidationError(
                "El nombre de usuario debe contener obligatoriamente Nombre y Apellido separados por un espacio."
            )

        # 2. Solo letras y espacios (bloquea números de forma estricta)
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', username):
            raise serializers.ValidationError(
                "El nombre de un profesor solo puede contener letras y espacios. No se permiten números ni caracteres especiales."
            )

        # 3. Adaptación interna para Django
        username_tecnico = username.replace(' ', '.').lower()

        # 4. Evitamos duplicados devolviendo un 400 limpio
        if User.objects.filter(username__iexact=username_tecnico).exists():
            raise serializers.ValidationError(
                "El nombre de usuario ya está registrado."
            )

        return username_tecnico

    
    def validate_birth_date(self, value):
        today = date.today()
        if value > today:
            raise serializers.ValidationError("La fecha de nacimiento no puede ser una fecha en el futuro.")
        
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18 or age > 65:
            raise serializers.ValidationError(
                f"El profesor debe tener entre 18 y 65 años de edad. Edad calculada: {age} años."
            )
        return value