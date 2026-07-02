"""
test_student_profile.py — Tests del perfil analítico del estudiante (onboarding)

Cubre:
  - GET /api/auth/me/ devuelve student_profile con onboarding_completo
  - PATCH /api/auth/profile/student/update/ actualiza los campos demográficos
  - Validación de choices inválidos
  - Campos read-only no se pueden modificar desde el endpoint

Correr:
    docker compose exec backend pytest users/tests_pytest/test_student_profile.py -v
"""

import pytest
from django.urls import reverse

from .fixtures import user, tokens, client_auth, client_anon, other_user  # noqa


# ── GET /api/auth/me/ incluye student_profile ─────────────────────────────────

@pytest.mark.django_db
def test_me_includes_student_profile_when_empty(client_auth):
    """Un usuario recién creado tiene student_profile con onboarding_completo=False."""
    response = client_auth.get(reverse('api_profile'))
    assert response.status_code == 200
    assert 'student_profile' in response.data
    sp = response.data['student_profile']
    assert sp['onboarding_completo'] is False
    assert sp['fecha_nacimiento'] is None
    assert sp['intereses'] == []


@pytest.mark.django_db
def test_me_onboarding_completo_true_after_update(client_auth):
    """Tras completar al menos un dato relevante, onboarding_completo pasa a True."""
    update_url = '/api/auth/profile/student/update/'
    client_auth.patch(update_url, {'objetivo_principal': 'estudios'}, format='json')

    response = client_auth.get(reverse('api_profile'))
    assert response.data['student_profile']['onboarding_completo'] is True


# ── PATCH /api/auth/profile/student/update/ ───────────────────────────────────

@pytest.mark.django_db
def test_update_student_profile_success(client_auth):
    """Actualización exitosa de todos los campos editables."""
    payload = {
        'fecha_nacimiento':      '1990-05-15',
        'nivel_educativo':       'secundario_completo',
        'estado_laboral':        'activo',
        'genero':                'F',
        'objetivo_principal':    'empleo',
        'disponibilidad_tiempo': 'media',
        'intereses':             ['Programación', 'Diseño'],
    }
    response = client_auth.patch('/api/auth/profile/student/update/', payload, format='json')
    assert response.status_code == 200
    assert response.data['nivel_educativo'] == 'secundario_completo'
    assert response.data['intereses'] == ['Programación', 'Diseño']


@pytest.mark.django_db
def test_update_student_profile_partial(client_auth):
    """PATCH parcial — solo actualiza el campo enviado, el resto queda igual."""
    client_auth.patch('/api/auth/profile/student/update/', {'genero': 'M'}, format='json')
    response = client_auth.patch('/api/auth/profile/student/update/', {'objetivo_principal': 'hobby'}, format='json')
    assert response.status_code == 200
    assert response.data['genero'] == 'M'
    assert response.data['objetivo_principal'] == 'hobby'


@pytest.mark.django_db
def test_update_student_profile_unauthorized(client_anon):
    """Sin token no se puede actualizar el perfil de estudiante."""
    response = client_anon.patch('/api/auth/profile/student/update/', {'genero': 'M'}, format='json')
    assert response.status_code == 401


# ── Validación de choices inválidos ────────────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.parametrize("campo,valor_invalido", [
    ('nivel_educativo',       'doctorado_completo'),
    ('estado_laboral',        'jubilado'),
    ('genero',                'X'),
    ('objetivo_principal',    'curiosidad'),
    ('disponibilidad_tiempo', 'extrema'),
])
def test_update_student_profile_invalid_choice(client_auth, campo, valor_invalido):
    """Rechaza valores que no están en las choices definidas para cada campo."""
    response = client_auth.patch('/api/auth/profile/student/update/', {campo: valor_invalido}, format='json')
    assert response.status_code == 400
    assert campo in response.data


# ── Campos read-only no se pueden modificar ───────────────────────────────────

@pytest.mark.django_db
@pytest.mark.parametrize("campo,valor", [
    ('racha_actual_dias',                999),
    ('racha_maxima_dias',                999),
    ('frecuencia_entradas',              999),
    ('tiempo_acumulado_app_minutos',     999.9),
    ('tiempo_interaccion_mentor_minutos',999.9),
    ('cantidad_videos_vistos',           999),
    ('tiempo_api_youtube_minutos',       999.9),
    ('desafios_completados',             999),
])
def test_readonly_fields_are_ignored(client_auth, campo, valor):
    """Los campos de analytics son read-only — el PATCH los ignora silenciosamente."""
    response = client_auth.patch('/api/auth/profile/student/update/', {campo: valor}, format='json')
    assert response.status_code == 200
    # El valor enviado no debe haberse aplicado (sigue en 0, el default)
    assert response.data[campo] != valor or response.data[campo] == 0


# ── Intereses como lista ──────────────────────────────────────────────────────

@pytest.mark.django_db
def test_intereses_accepts_empty_list(client_auth):
    """Intereses puede ser una lista vacía sin error."""
    response = client_auth.patch('/api/auth/profile/student/update/', {'intereses': []}, format='json')
    assert response.status_code == 200
    assert response.data['intereses'] == []


@pytest.mark.django_db
def test_intereses_accepts_custom_values(client_auth):
    """Intereses acepta valores libres, no limitados a una lista predefinida."""
    custom = ['Robótica avanzada', 'Apicultura']
    response = client_auth.patch('/api/auth/profile/student/update/', {'intereses': custom}, format='json')
    assert response.status_code == 200
    assert response.data['intereses'] == custom
