from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from users.models import UserProfile 
from django.db import connection

class MyEnrollmentsAPITest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Crear el procedimiento almacenado en la DB de tests
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE OR REPLACE FUNCTION sp_get_my_enrollments(p_student_email VARCHAR)
                RETURNS TABLE (
                    enrollment_id INTEGER, 
                    student_email VARCHAR, 
                    course_name VARCHAR, 
                    professor_name VARCHAR
                ) AS $$
                BEGIN
                    RETURN QUERY
                    SELECT 
                        e.id::INTEGER,
                        u_student.email::VARCHAR,
                        c.title::VARCHAR,
                        u_prof.username::VARCHAR
                    FROM enrollment_enrollment e
                    INNER JOIN auth_user u_student ON e.student_id = u_student.id
                    INNER JOIN courses c ON e.course_id = c.id
                    INNER JOIN auth_user u_prof ON c.professor_id = u_prof.id
                    WHERE u_student.email = p_student_email;
                END;
                $$ LANGUAGE plpgsql;
            """)

    def setUp(self):
        # 1. Crear usuarios
        self.student = User.objects.create_user(username='student', email='student@test.com', password='password')
        self.admin = User.objects.create_user(username='admin', email='admin@test.com', password='password')
        
        # 2. Actualizar perfiles existentes (creados por señales)
        self.profile = UserProfile.objects.get(user=self.student)
        self.profile.role = 'STUDENT'
        self.profile.save()
        
        self.admin_profile = UserProfile.objects.get(user=self.admin)
        self.admin_profile.role = 'ADMIN'
        self.admin_profile.save()
        
        self.url = reverse('enrollment:my-enrollments')

    def test_get_my_enrollments_as_student(self):
        """Verifica que un estudiante pueda acceder a sus inscripciones."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_my_enrollments_as_admin_forbidden(self):
        """Verifica que un admin no pueda acceder (debe dar 403 Forbidden)."""
        # 1. Aseguramos el rol justo antes de la petición
        self.admin.profile.role = 'ADMIN'
        self.admin.profile.save()
        
        # 2. Autenticamos y probamos
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        
        # 3. Debe dar 403 correctamente
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access(self):
        """Verifica que un usuario no logueado reciba un 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EnrollStudentAPITest(APITestCase):
    """
    Regresión: un alumno que ya está inscripto en un curso y vuelve a mandar
    POST /enrollment/enroll/ para el mismo curso NO debe pisar/renovar su
    inscripción existente — debe rechazarse con 400 y el mensaje
    'Ya estas anotado en este curso.', y no debe crearse una segunda fila.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # sp_enroll_student ya se crea vía la migración enrollment/0002, pero
        # reforzamos acá por si el entorno de test corre con --keepdb viejo.
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_proc WHERE proname = 'sp_enroll_student'")
            if not cursor.fetchone():
                raise AssertionError(
                    "sp_enroll_student no existe en la DB de test — "
                    "falta correr las migraciones de enrollment (0002_load_stored_procedures)."
                )

    def setUp(self):
        from courses.models import Course

        self.student = User.objects.create_user(username='alumno', email='alumno@test.com', password='password')
        self.profile = UserProfile.objects.get(user=self.student)
        self.profile.role = 'STUDENT'
        self.profile.save()

        self.professor = User.objects.create_user(username='profe', email='profe@test.com', password='password')

        self.course = Course.objects.create(
            professor=self.professor,
            title='Curso de prueba',
            is_active=True,
        )
        self.url = reverse('enrollment:enroll-student')

    def test_reenroll_same_course_is_rejected_not_overwritten(self):
        self.client.force_authenticate(user=self.student)

        first = self.client.post(self.url, {'course_id': self.course.id}, format='json')
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(self.url, {'course_id': self.course.id}, format='json')
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Ya estas anotado en este curso.', str(second.data))

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM enrollment_enrollment WHERE student_id = %s AND course_id = %s",
                [self.student.id, self.course.id],
            )
            count = cursor.fetchone()[0]
        self.assertEqual(count, 1, "La reinscripción no debe crear/pisar una segunda fila.")