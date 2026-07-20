"""
users/tests.py — Suite de tests para los endpoints de autenticación y perfil.

Cómo correr los tests:
----------------------

1. Tests básicos con output en consola:
   docker compose exec backend python manage.py test users --verbosity=2

2. Generar reporte HTML (requiere pytest y pytest-html):

   # Instalar dependencias (solo la primera vez)
   docker compose exec backend pip install pytest pytest-django pytest-html

   # Correr y generar reporte
   docker compose exec backend pytest users/tests.py --html=/app/test-reports/report.html --self-contained-html

   # Copiar el reporte al host
   docker cp <nombre_contenedor_backend>:/app/test-reports/report.html ./test-reports/

   # Abrir report.html en el browser

3. Generar reporte TXT simple:
   docker compose exec backend python manage.py test users --verbosity=2 2>&1 | tee test-report.txt

Notas para QA:
--------------
- El modelo de usuario es auth.User con UserProfile y UserConfig como OneToOne (creados por señales)
- Autenticación: JWT (Bearer token) — NO Token DRF
- Login se hace por EMAIL, no por username
- El usuario de prueba setUp tiene is_staff=True para poder testear api_users_list
- Todos los endpoints de perfil usan Bearer <access_token> en el header Authorization
"""

from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from django.core import mail
from django.test import override_settings
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserActivityLog


class ImmediateThread:
    """Reemplazo sincrónico de threading.Thread para tests: corre el target
    al toque en vez de en un hilo aparte, así los asserts sobre el resultado
    (ej. mail.outbox) son deterministas y no dependen de timing."""
    def __init__(self, target=None, args=(), kwargs=None, daemon=None):
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}

    def start(self):
        self.target(*self.args, **self.kwargs)


@patch('users.models.threading.Thread', ImmediateThread)
class UserEndpointsTestCase(APITestCase):

    def setUp(self):
        """
        Crea el usuario de prueba base con perfil y config de accesibilidad.
        is_staff=True es necesario para el test de listado de usuarios.
        """
        # LoginRateThrottle/RegisterRateThrottle usan el cache por defecto
        # (LocMemCache), que persiste entre tests dentro de la misma corrida.
        # Sin este clear(), tests que llaman a login/register muchas veces
        # en la suite completa pueden empezar a devolver 429 sin motivo.
        cache.clear()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123!',
            email='testuser@example.com',
            is_staff=True,
        )

        # Actualizar perfil (creado automáticamente por señal post_save)
        self.user.profile.phone      = '123456789'
        self.user.profile.avatar_url = 'http://example.com/avatar.jpg'
        self.user.profile.role       = 'STUDENT'
        self.user.profile.save()

        # Actualizar config de accesibilidad (creada automáticamente por señal post_save)
        self.user.config.font_size      = 'MEDIUM'
        self.user.config.high_contrast  = False
        self.user.config.voice_guidance = False
        self.user.config.save()

        # Generar tokens JWT para los tests autenticados
        self.refresh           = RefreshToken.for_user(self.user)
        self.access_token      = str(self.refresh.access_token)
        self.refresh_token_str = str(self.refresh)

        # create_user() de arriba dispara send_email_post_register (post_save
        # sobre User) para 'testuser' en TODOS los tests de esta clase, no
        # solo en los que prueban registro. Sin este clear(), cualquier test
        # que después revise mail.outbox arranca con ese email ya adentro.
        mail.outbox = []

    # ── REGISTRO ──────────────────────────────────────────────────────────────

    def test_api_register_success(self):
        """Registro exitoso con todos los campos opcionales incluidos."""
        url  = reverse('api_register')
        data = {
            'username':         'newuser',
            'password':         'Newpassword123!',
            'password_confirm': 'Newpassword123!',
            'email':            'newuser@example.com',
            'phone':            '987654321',
            'avatar_url':       'http://example.com/new_avatar.jpg',
            'font_size':        'LARGE',
            'high_contrast':    True,
            'voice_guidance':   True,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')
        self.assertEqual(response.data['user']['phone'], '987654321')
        self.assertEqual(response.data['user']['config']['font_size'], 'LARGE')
        self.assertTrue(response.data['user']['config']['high_contrast'])

    def test_api_register_password_mismatch(self):
        """El registro falla si password y password_confirm no coinciden."""
        url  = reverse('api_register')
        data = {
            'username':         'newuser',
            'password':         'Newpassword123!',
            'password_confirm': 'Differentpassword123!',
            'email':            'newuser@example.com',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password_confirm'], ['Las contraseñas ingresadas no coinciden.'])

    def test_api_register_weak_password(self):
        """El registro falla si la contraseña no cumple requisitos OWASP."""
        url  = reverse('api_register')
        data = {
            'username':         'newuser',
            'password':         'weak',
            'password_confirm': 'weak',
            'email':            'newuser@example.com',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['password'],
            ['La contraseña debe contener mínimo 8 caracteres, una mayúscula, un número y un carácter especial.']
        )

    def test_api_register_duplicate_email(self):
        """El registro falla si el email ya está registrado."""
        url  = reverse('api_register')
        data = {
            'username':         'newuser',
            'password':         'Newpassword123!',
            'password_confirm': 'Newpassword123!',
            'email':            'testuser@example.com',  # Ya existe en setUp
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'], ['Este correo electrónico ya se encuentra registrado.'])

    def test_api_register_missing_fields(self):
        """El registro falla si faltan campos obligatorios."""
        url      = reverse('api_register')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'],         ['El username es un campo obligatorio.'])
        self.assertEqual(response.data['email'],            ['El email es un campo obligatorio.'])
        self.assertEqual(response.data['password'],         ['El password es un campo obligatorio.'])
        self.assertEqual(response.data['password_confirm'], ['El password_confirm es un campo obligatorio.'])

    def test_api_register_invalid_phone(self):
        """El registro falla si el teléfono tiene formato inválido."""
        url  = reverse('api_register')
        data = {
            'username':         'badphoneuser',
            'password':         'Newpassword123!',
            'password_confirm': 'Newpassword123!',
            'email':            'badphone@example.com',
            'phone':            'abcde',  # Formato inválido
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)

    def test_api_register_invalid_font_size(self):
        """El registro falla si font_size no es SMALL, MEDIUM o LARGE."""
        url  = reverse('api_register')
        data = {
            'username':         'fontuser',
            'password':         'Newpassword123!',
            'password_confirm': 'Newpassword123!',
            'email':            'fontuser@example.com',
            'font_size':        'XLARGE',  # Valor inválido
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('font_size', response.data)
        self.assertEqual(
            response.data['font_size'],
            ['El tamaño de fuente seleccionado no es válido. Las opciones permitidas son: SMALL, MEDIUM, LARGE.']
        )

    # ── LOGIN ─────────────────────────────────────────────────────────────────

    def test_api_login_success(self):
        """Login exitoso con email y password válidos. Devuelve JWT."""
        url  = reverse('api_login')
        data = {'email': 'testuser@example.com', 'password': 'testpassword123!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_api_login_invalid_credentials(self):
        """Login falla con contraseña incorrecta."""
        url  = reverse('api_login')
        data = {'email': 'testuser@example.com', 'password': 'wrongpassword!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Credenciales inválidas.')

    def test_api_login_missing_fields(self):
        """Login falla si faltan campos obligatorios."""
        url      = reverse('api_login')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'],    ['El email es un campo obligatorio.'])
        self.assertEqual(response.data['password'], ['El password es un campo obligatorio.'])

    # ── PERFIL ────────────────────────────────────────────────────────────────

    def test_api_profile_unauthorized(self):
        """El perfil requiere autenticación — devuelve 401 sin token."""
        url      = reverse('api_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_profile_get_success(self):
        """GET del perfil devuelve datos del usuario autenticado."""
        url = reverse('api_profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['phone'],    '123456789')
        self.assertEqual(response.data['config']['font_size'], 'MEDIUM')

    def test_api_profile_update_put_success(self):
        """PUT actualiza email, teléfono, avatar y config de accesibilidad."""
        url  = reverse('api_profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            'email':          'updated@example.com',
            'phone':          '111222333',
            'avatar_url':     'http://example.com/updated.png',
            'font_size':      'SMALL',
            'high_contrast':  True,
            'voice_guidance': True,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'],  'updated@example.com')
        self.assertEqual(response.data['user']['phone'],  '111222333')
        self.assertEqual(response.data['user']['config']['font_size'], 'SMALL')
        self.assertTrue(response.data['user']['config']['high_contrast'])

    def test_api_profile_update_patch_success(self):
        """PATCH actualiza solo los campos enviados, el resto no cambia."""
        url  = reverse('api_profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {'phone': '999888777'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['phone'], '999888777')
        self.assertEqual(response.data['user']['config']['font_size'], 'MEDIUM')  # Sin cambios

    def test_api_profile_update_duplicate_email_blocked(self):
        """El perfil no puede actualizarse con un email ya registrado por otro usuario."""
        User.objects.create_user(
            username='otheruser',
            password='password123!',
            email='taken@example.com',
        )
        url  = reverse('api_profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {'email': 'taken@example.com', 'phone': '111222333'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'El correo electrónico ya está registrado.')

    # ── LISTADO DE USUARIOS ───────────────────────────────────────────────────

    def test_api_users_list_success(self):
        """Solo staff puede listar usuarios. Devuelve respuesta paginada."""
        User.objects.create_user(
            username='anotheruser',
            password='anotherpassword',
            email='another@example.com',
        )
        url = reverse('api_users_list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)

    # ── LOGOUT ────────────────────────────────────────────────────────────────

    def test_api_logout_success(self):
        """Logout invalida el refresh token enviado en el body."""
        url  = reverse('api_logout')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {'refresh': self.refresh_token_str}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ── ESTUDIANTE ANALYTICS PROFILE ──────────────────────────────────────────

    def test_api_update_student_profile_success(self):
        """PATCH actualiza los campos demográficos y de intereses de StudentProfile."""
        url = reverse('update-student-profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            'education_level': 'secundario_completo',
            'employment_status': 'activo',
            'user_gender': 'ND',
            'primary_objective': 'empleo',
            'time_availability': 'alta',
            'user_interests': ['Programación', 'Ciencia de Datos']
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['education_level'], 'secundario_completo')
        self.assertEqual(response.data['employment_status'], 'activo')
        self.assertEqual(response.data['user_gender'], 'ND')
        self.assertEqual(response.data['primary_objective'], 'empleo')
        self.assertEqual(response.data['time_availability'], 'alta')
        self.assertEqual(response.data['user_interests'], ['Programación', 'Ciencia de Datos'])

    def test_api_update_student_profile_unauthorized(self):
        """El endpoint requiere autenticación — devuelve 401 sin token."""
        url = reverse('update-student-profile')
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_update_student_profile_read_only_fields(self):
        """Los campos de analítica marcados como read_only no deben poder ser modificados."""
        url = reverse('update-student-profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            'app_time_min': 999.9,
            'current_streak_days': 50,
            'watched_videos_count': 100
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # El perfil del estudiante en la base de datos debe seguir con los valores por defecto (0)
        self.assertEqual(response.data['app_time_min'], 0.0)
        self.assertEqual(response.data['current_streak_days'], 0)
        self.assertEqual(response.data['watched_videos_count'], 0)

    # ── AUDITORÍA DE SESIÓN (UserActivityLog) ─────────────────────────────────

    def test_api_login_creates_activity_log_and_online_status(self):
        """Login exitoso debe registrar un UserActivityLog de tipo LOGIN y
        marcar session_status='ONLINE' en el perfil."""
        url  = reverse('api_login')
        data = {'email': 'testuser@example.com', 'password': 'testpassword123!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            UserActivityLog.objects.filter(user=self.user, event_type='login').exists()
        )
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.session_status, 'ONLINE')

    def test_api_logout_creates_activity_log_and_offline_status(self):
        """Logout debe registrar un UserActivityLog de tipo LOGOUT y marcar
        session_status='OFFLINE', incluso si el refresh token ya no es válido
        (la escritura del log no depende de que el blacklist tenga éxito)."""
        url  = reverse('api_logout')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {'refresh': self.refresh_token_str}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            UserActivityLog.objects.filter(user=self.user, event_type='logout').exists()
        )
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.session_status, 'OFFLINE')

    # ── RATE LIMITING (throttling) ────────────────────────────────────────────

    def test_api_login_rate_limited_after_3_attempts(self):
        """LoginRateThrottle: al 4to intento en el mismo minuto, devuelve 429
        sin importar si las credenciales son correctas o no."""
        url  = reverse('api_login')
        data = {'email': 'testuser@example.com', 'password': 'wrongpassword!'}
        for _ in range(3):
            response = self.client.post(url, data, format='json')
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_api_register_rate_limited_after_3_attempts(self):
        """RegisterRateThrottle: al 4to intento en el mismo minuto, devuelve
        429 — protege contra alta masiva de cuentas."""
        url  = reverse('api_register')
        data = {
            'username': 'ratelimited',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'email': 'ratelimited@example.com',
        }
        for _ in range(3):
            response = self.client.post(url, data, format='json')
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_login_and_register_throttles_are_independent(self):
        """LoginRateThrottle y RegisterRateThrottle deben tener scopes propios
        ('login'/'register'), no compartir el balde 'anon' por default de
        AnonRateThrottle — si lo compartieran, alternar entre los dos
        endpoints agotaría el límite combinado en vez de 3 + 3 independientes."""
        login_url    = reverse('api_login')
        register_url = reverse('api_register')
        login_data   = {'email': 'testuser@example.com', 'password': 'wrongpassword!'}

        for i in range(3):
            response = self.client.post(login_url, login_data, format='json')
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

            register_data = {
                'username': f'indep{i}',
                'password': 'Password123!',
                'password_confirm': 'Password123!',
                'email': f'indep{i}@example.com',
            }
            response = self.client.post(register_url, register_data, format='json')
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_api_register_sends_welcome_email(self):
        """Al registrarse, la señal send_email_post_register debe encolar un
        mail de bienvenida al address del usuario nuevo. Se parchea
        threading.Thread para que corra sincrónico y el assert sea
        determinista (sin sleep/polling)."""
        url  = reverse('api_register')
        data = {
            'username': 'nuevoconemail',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'email': 'nuevoconemail@example.com',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['nuevoconemail@example.com'])
        self.assertIn('Bienvenido', mail.outbox[0].subject)


