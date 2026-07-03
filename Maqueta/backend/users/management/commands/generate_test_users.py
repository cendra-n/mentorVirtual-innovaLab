"""
Management command para generar usuarios de prueba con datos realistas.

Uso:
    docker compose exec backend python manage.py generate_test_users
    docker compose exec backend python manage.py generate_test_users --count 50
    docker compose exec backend python manage.py generate_test_users --count 20 --role PROFESSOR
"""
import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import StudentProfile

NOMBRES = [
    'Juan', 'María', 'Carlos', 'Ana', 'Pedro', 'Laura', 'Diego', 'Sofía',
    'Martín', 'Lucía', 'Fernando', 'Camila', 'Roberto', 'Valentina', 'Pablo',
    'Florencia', 'Gabriel', 'Julieta', 'Sebastián', 'Agustina',
]

APELLIDOS = [
    'González', 'Rodríguez', 'Gómez', 'Fernández', 'López', 'Díaz', 'Martínez',
    'Pérez', 'García', 'Sánchez', 'Romero', 'Sosa', 'Torres', 'Álvarez', 'Ruiz',
]

NIVELES_EDUCATIVOS = [
    'primario_completo', 'primario_incompeto', 'secundario_incompleto',
    'secundario_completo', 'terciario_incompleto', 'terciario_en_curso',
    'terciario_completo', 'universitario_incompleto', 'universitario_en_curso',
    'universitario_completo',
]

ESTADOS_LABORALES = ['activo', 'desempleado']
GENEROS = ['M', 'F', 'ND']
OBJETIVOS = ['empleo', 'personal', 'estudios', 'hobby']
DISPONIBILIDADES = ['baja', 'media', 'alta']

INTERESES_POOL = [
    'Programación', 'Diseño', 'Cocina', 'Idiomas', 'Música', 'Manualidades',
    'Finanzas', 'Salud', 'Oficios', 'Tecnología', 'Jardinería', 'Fotografía',
]


class Command(BaseCommand):
    help = 'Genera usuarios de prueba con perfiles completos para testing y demos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', type=int, default=20,
            help='Cantidad de usuarios a generar (default: 20)',
        )
        parser.add_argument(
            '--role', type=str, default='STUDENT',
            choices=['STUDENT', 'PROFESSOR', 'ADMIN'],
            help='Rol a asignar a los usuarios generados (default: STUDENT)',
        )
        parser.add_argument(
            '--password', type=str, default='Test1234!',
            help='Contraseña para todos los usuarios generados (default: Test1234!)',
        )
        parser.add_argument(
            '--onboarding-completo', action='store_true',
            help='Si se pasa, completa el onboarding (StudentProfile) con datos random.',
        )
        parser.add_argument(
            '--clear', action='store_true',
            help='Elimina usuarios de prueba previos (username empieza con "test_") antes de generar.',
        )

    def handle(self, *args, **options):
        count    = options['count']
        role     = options['role']
        password = options['password']
        onboarding_completo = options['onboarding_completo']
        clear    = options['clear']

        if clear:
            deleted, _ = User.objects.filter(username__startswith='test_').delete()
            self.stdout.write(self.style.WARNING(f'🗑️  Eliminados {deleted} usuarios de prueba previos.'))

        created = 0
        for i in range(count):
            nombre   = random.choice(NOMBRES)
            apellido = random.choice(APELLIDOS)
            suffix   = random.randint(1000, 9999)
            username = f"test_{nombre.lower()}{apellido.lower()}{suffix}"
            email    = f"{username}@testmentor.com"

            if User.objects.filter(username=username).exists():
                continue

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido,
                is_staff=(role == 'ADMIN'),
            )

            # El perfil y config se crean por señal — actualizamos el rol
            if hasattr(user, 'profile'):
                user.profile.role = role
                user.profile.avatar_url = f'https://i.pravatar.cc/150?img={random.randint(1, 70)}'
                user.profile.phone = f'+549{random.randint(1000000000, 9999999999)}'[:13]
                user.profile.save()

            # Completar StudentProfile si se pidió
            if onboarding_completo and hasattr(user, 'student_analytics'):
                sp = user.student_analytics
                edad_anios = random.randint(18, 70)
                sp.fecha_nacimiento = date.today() - timedelta(days=edad_anios * 365)
                sp.nivel_educativo = random.choice(NIVELES_EDUCATIVOS)
                sp.estado_laboral = random.choice(ESTADOS_LABORALES)
                sp.genero = random.choice(GENEROS)
                sp.objetivo_principal = random.choice(OBJETIVOS)
                sp.disponibilidad_tiempo = random.choice(DISPONIBILIDADES)
                sp.intereses = random.sample(INTERESES_POOL, k=random.randint(1, 4))
                sp.racha_actual_dias = random.randint(0, 30)
                sp.racha_maxima_dias = max(sp.racha_actual_dias, random.randint(0, 60))
                sp.frecuencia_entradas = random.randint(0, 100)
                sp.tiempo_acumulado_app_minutos = round(random.uniform(0, 500), 1)
                sp.cantidad_videos_vistos = random.randint(0, 50)
                sp.desafios_completados = random.randint(0, 20)
                sp.save()

            created += 1
            self.stdout.write(f'  ✓ {username} ({role}) — {email}')

        self.stdout.write(self.style.SUCCESS(
            f'\n✨ {created} usuarios creados exitosamente con password "{password}"'
        ))
