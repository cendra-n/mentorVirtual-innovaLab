# users/tests_professor.py
from datetime import date
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

class AdminCreateProfessorTests(APITestCase):

    def setUp(self):
        # 1. Aseguramos un usuario administrador para pegarle al endpoint
        self.admin_user = User.objects.create_superuser(
            username='admin.test',
            email='admin@test.com',
            password='Password123!'
        )
        
        # 2. Forzamos la autenticación de Staff para que IsAdminUser nos deje pasar
        self.client.force_authenticate(user=self.admin_user)
        
        # 3. Seteamos la URL real unificada del proyecto
        self.url = '/api/admin/users/create-professor/'
        
        self.valid_payload = {
            "username": "Carlos Gomez",
            "email": "carlos.gomez@example.com",
            "password": "SecurePassword1!",
            "dni": "30456123",
            "address": "25 de Mayo 1424, CABA",
            "birth_date": "1985-05-10",
            "phone": "1122334455",
            "avatar_url": "",
            "title_degree": "Ingeniero en Sistemas"
        }

    def test_create_professor_success(self):
        """Valida que un administrador cree exitosamente un profesor con datos íntegros."""
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_professor_future_date_fails(self):
        """Verifica que el serializador bloquee fechas de nacimiento en el futuro."""
        payload = self.valid_payload.copy()
        # Forzamos un año en el futuro para que salte la validación del > today sin depender del día
        payload["birth_date"] = str(date.today().replace(year=date.today().year + 1))
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_professor_too_young_fails(self):
        """Bloquea el intento si el profesor tiene menos de 18 años."""
        payload = self.valid_payload.copy()
        payload["birth_date"] = str(date.today().replace(year=date.today().year - 17))
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_professor_too_old_fails(self):
        """Bloquea el intento si la edad del profesor supera los 65 años."""
        payload = self.valid_payload.copy()
        payload["birth_date"] = str(date.today().replace(year=date.today().year - 66))
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_professor_duplicate_username_case_insensitive(self):
        """Prueba que el validador __iexact bloquee duplicados idénticos en texto."""
        self.client.post(self.url, self.valid_payload, format='json')
        
        payload = self.valid_payload.copy()
        payload["email"] = "otro.email@test.com"
        payload["dni"] = "99999999"
        payload["username"] = "cArLoS gOmEz"
        
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)