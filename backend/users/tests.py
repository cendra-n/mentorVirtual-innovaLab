from .models import UserProfile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

class UserEndpointsTestCase(APITestCase):

    def setUp(self):
        # Crear un usuario de prueba inicial
        self.user = UserProfile.objects.create_user(
            username='testuser',
            password='testpassword123!',
            email='testuser@example.com'
        )
        # Configurar perfil y config del usuario (creados por las señales)
        self.user.phone = '123456789'
        self.user.avatar_url = 'http://example.com/avatar.jpg'
        self.user.role = 'STUDENT'
        self.user.save()

        # 3. La señal ya creó el config, lo editamos directo
        self.user.config.font_size = 'MEDIUM'
        self.user.config.high_contrast = False
        self.user.config.voice_guidance = False
        self.user.config.save()

        # Obtener el token para el usuario de prueba
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token_str = str(self.refresh)
        
    def test_api_register_success(self):
        url = reverse('api_register')
        data = {
            'username': 'newuser',
            'password': 'Newpassword123!',
            'password_confirm': 'Newpassword123!',
            'email': 'newuser@example.com',
            'phone': '987654321',
            'avatar_url': 'http://example.com/new_avatar.jpg',
            'font_size': 'LARGE',
            'high_contrast': True,
            'voice_guidance': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')
        self.assertEqual(response.data['user']['phone'], '987654321')
        self.assertEqual(response.data['user']['config']['font_size'], 'LARGE')
        self.assertTrue(response.data['user']['config']['high_contrast'])

    def test_api_register_password_mismatch(self):
        url = reverse('api_register')
        data = {
            'username': 'newuser',
            'password': 'Newpassword123!',
            'password_confirm': 'Differentpassword123!',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password_confirm'], ['Las contraseñas ingresadas no coinciden.'])

    def test_api_register_weak_password(self):
        url = reverse('api_register')
        data = {
            'username': 'newuser',
            'password': 'weak',
            'password_confirm': 'weak',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'], ['La contraseña debe contener un mínimo 8 caracteres, al menos una mayúscula, un número y un carácter especial.'])

    def test_api_register_duplicate_email(self):
        url = reverse('api_register')
        data = {
            'username': 'newuser',
            'password': 'Newpassword123!',
            'password_confirm': 'Newpassword123!',
            'email': 'testuser@example.com'  # Ya registrado en setUp
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'], ['Este correo electrónico ya se encuentra registrado.'])

    def test_api_register_missing_fields(self):
        url = reverse('api_register')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'], ['El username es un campo obligatorio.'])
        self.assertEqual(response.data['email'], ['El email es un campo obligatorio.'])
        self.assertEqual(response.data['password'], ['El password es un campo obligatorio.'])
        self.assertEqual(response.data['password_confirm'], ['El password_confirm es un campo obligatorio.'])

    def test_api_login_success(self):
        url = reverse('api_login')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_api_login_invalid_credentials(self):
        url = reverse('api_login')
        data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Credenciales inválidas.')

    def test_api_login_missing_fields(self):
        url = reverse('api_login')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'], ['El email es un campo obligatorio.'])
        self.assertEqual(response.data['password'], ['El password es un campo obligatorio.'])

    def test_api_profile_unauthorized(self):
        url = reverse('api_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_profile_get_success(self):
        url = reverse('api_profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['phone'], '123456789')
        self.assertEqual(response.data['config']['font_size'], 'MEDIUM')

    def test_api_profile_update_put_success(self):
        url = reverse('api_profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            'email': 'updated@example.com',
            'phone': '111222333',
            'avatar_url': 'http://example.com/updated.png',
            'font_size': 'SMALL',
            'high_contrast': True,
            'voice_guidance': True
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'updated@example.com')
        self.assertEqual(response.data['user']['phone'], '111222333')
        self.assertEqual(response.data['user']['config']['font_size'], 'SMALL')
        self.assertTrue(response.data['user']['config']['high_contrast'])

    def test_api_profile_update_patch_success(self):
        url = reverse('api_profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        data = {
            'phone': '999888777'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['phone'], '999888777')
        self.assertEqual(response.data['user']['config']['font_size'], 'MEDIUM') # Remains unchanged

    def test_api_users_list_success(self):
        # Crear un segundo usuario
        UserProfile.objects.create_user(
            username='anotheruser',
            password='anotherpassword',
            email='another@example.com'
        )
        url = reverse('api_users_list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificamos la estructura paginada
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['username'], 'testuser')
        self.assertEqual(response.data['results'][1]['username'], 'anotheruser')

    def test_api_logout_success(self):
        url = reverse('api_logout')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        
        # Le enviamos el refresh token en el cuerpo de la petición como espera la vista
        data = {'refresh': self.refresh_token_str}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_api_register_invalid_phone(self):
        url = reverse('api_register')
        data = {
            'username': 'badphoneuser',
            'password': 'Newpassword123!',
            'password_confirm': 'Newpassword123!',
            'email': 'badphone@example.com',
            'phone': 'abcde'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)

    def test_api_register_invalid_font_size(self):
        url = reverse('api_register')
        data = {
            'username': 'fontuser',
            'password': 'Newpassword123!',
            'password_confirm': 'Newpassword123!',
            'email': 'fontuser@example.com',
            'font_size': 'XLARGE' 
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('font_size', response.data)
        self.assertEqual(
            response.data['font_size'], 
            ['El tamaño de fuente seleccionado no es válido. Las opciones permitidas son: SMALL, MEDIUM, LARGE.']
        )
        
    def test_api_profile_update_duplicate_email_blocked(self):
        UserProfile.objects.create_user(
            username='otheruser',
            password='password123!',
            email='taken@example.com'
        )
        
        url = reverse('api_profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        
        data = {
            'email': 'taken@example.com',
            'phone': '111222333'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'El correo electrónico ya está registrado.')