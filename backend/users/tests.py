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
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class UserEndpointsTestCase(APITestCase):

    def setUp(self):
        """
        Crea el usuario de prueba base con perfil y config de accesibilidad.
        is_staff=True es necesario para el test de listado de usuarios.
        """
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
            'nivel_educativo': 'secundario_completo',
            'estado_laboral': 'activo',
            'genero': 'ND',
            'objetivo_principal': 'empleo',
            'disponibilidad_tiempo': 'alta',
            'intereses': ['Programación', 'Ciencia de Datos']
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nivel_educativo'], 'secundario_completo')
        self.assertEqual(response.data['estado_laboral'], 'activo')
        self.assertEqual(response.data['genero'], 'ND')
        self.assertEqual(response.data['objetivo_principal'], 'empleo')
        self.assertEqual(response.data['disponibilidad_tiempo'], 'alta')
        self.assertEqual(response.data['intereses'], ['Programación', 'Ciencia de Datos'])

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
            'tiempo_acumulado_app_minutos': 999.9,
            'racha_actual_dias': 50,
            'cantidad_videos_vistos': 100
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # El perfil del estudiante en la base de datos debe seguir con los valores por defecto (0)
        self.assertEqual(response.data['tiempo_acumulado_app_minutos'], 0.0)
        self.assertEqual(response.data['racha_actual_dias'], 0)
        self.assertEqual(response.data['cantidad_videos_vistos'], 0)

