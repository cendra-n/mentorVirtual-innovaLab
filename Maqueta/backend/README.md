# Herramientas de Testing — Mentor Virtual

Este módulo contiene herramientas para generar datos de prueba y testear el
sistema de perfiles de estudiante (onboarding, analytics).

---

## 📁 Estructura y dónde copiar

```
backend/users/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── generate_test_users.py    ← Generador de usuarios de prueba
└── tests_pytest/
    └── test_student_profile.py        ← Tests del StudentProfile
```

Copiá la carpeta `management/` completa dentro de `backend/users/` y el archivo
`test_student_profile.py` dentro de `backend/users/tests_pytest/`.

No requiere ningún cambio en `INSTALLED_APPS` ni `settings.py` — Django detecta
los management commands automáticamente por estar dentro de `management/commands/`
en una app ya instalada.

---

## 🧑‍🎓 Generador de usuarios de prueba

### Uso básico

```bash
# 20 alumnos con password Test1234! (default)
docker compose exec backend python manage.py generate_test_users
```

### Opciones disponibles

| Flag | Default | Descripción |
|------|---------|-------------|
| `--count N` | `20` | Cantidad de usuarios a generar |
| `--role ROL` | `STUDENT` | `STUDENT`, `PROFESSOR` o `ADMIN` |
| `--password PASS` | `Test1234!` | Contraseña para todos los usuarios generados |
| `--onboarding-completo` | (no) | Si se pasa, completa el `StudentProfile` con datos demográficos y analytics random |
| `--clear` | (no) | Borra usuarios de prueba previos (`username` empieza con `test_`) antes de generar |

### Ejemplos

```bash
# 50 alumnos con perfil de onboarding completo (para ver datos en analytics)
docker compose exec backend python manage.py generate_test_users --count 50 --onboarding-completo

# 5 profesores de prueba
docker compose exec backend python manage.py generate_test_users --count 5 --role PROFESSOR

# Limpiar todo y regenerar con un set nuevo
docker compose exec backend python manage.py generate_test_users --clear --count 30 --onboarding-completo
```

### Qué genera

- `username` único con formato `test_{nombre}{apellido}{4digitos}` (ej: `test_juangonzalez4821`)
- `email` correspondiente en `@testmentor.com`
- Perfil (`UserProfile`) con rol, avatar (pravatar.cc) y teléfono random
- Si se pasa `--onboarding-completo`:
  - Fecha de nacimiento (entre 18 y 70 años)
  - Nivel educativo, estado laboral, género, objetivo principal, disponibilidad — todos random dentro de las choices válidas
  - 1 a 4 intereses random
  - Métricas de analytics (racha, frecuencia, tiempo en app, videos vistos, desafíos) con valores random

### Cómo verificar los datos generados

```bash
# Conectarse a psql
docker exec <nombre_contenedor_postgres> psql -U postgres -d mentor_virtual

# Ver los usuarios de prueba con su perfil
SELECT u.username, u.email, p.role, sp.nivel_educativo, sp.objetivo_principal, sp.intereses
FROM auth_user u
LEFT JOIN users_userprofile p ON p.user_id = u.id
LEFT JOIN users_studentprofile sp ON sp.user_id = u.id
WHERE u.username LIKE 'test_%'
ORDER BY u.id DESC
LIMIT 20;

# Contar cuántos hay
SELECT COUNT(*) FROM auth_user WHERE username LIKE 'test_%';
```

### Borrar todos los usuarios de prueba

```bash
docker compose exec backend python manage.py generate_test_users --clear --count 0
```

(El `--count 0` evita generar usuarios nuevos, solo ejecuta la limpieza.)

---

## 🧪 Tests de StudentProfile

### Uso

```bash
# Correr solo estos tests
docker compose exec backend pytest users/tests_pytest/test_student_profile.py -v

# Con reporte HTML
docker compose exec backend pytest users/tests_pytest/test_student_profile.py \
  --html=/app/test-reports/student_profile_report.html --self-contained-html -v
```

### Qué cubre (11 tests)

| Test | Verifica |
|------|----------|
| `test_me_includes_student_profile_when_empty` | `/api/auth/me/` devuelve `student_profile` con `onboarding_completo: false` para un usuario nuevo |
| `test_me_onboarding_completo_true_after_update` | Tras completar un dato, `onboarding_completo` pasa a `true` |
| `test_update_student_profile_success` | PATCH exitoso con todos los campos |
| `test_update_student_profile_partial` | PATCH parcial respeta los campos no enviados |
| `test_update_student_profile_unauthorized` | Sin token → 401 |
| `test_update_student_profile_invalid_choice` (×5) | Rechaza valores fuera de las choices válidas en cada campo |
| `test_readonly_fields_are_ignored` (×8) | Los campos de analytics no se pueden modificar desde el PATCH |
| `test_intereses_accepts_empty_list` | `intereses: []` no da error |
| `test_intereses_accepts_custom_values` | `intereses` acepta valores libres, no limitados a una lista fija |

### Requisitos previos

Estos tests dependen de los fixtures ya existentes en `users/tests_pytest/fixtures.py`
(`user`, `client_auth`, `client_anon`, `other_user`) — no requieren ningún fixture nuevo.

Asumen que el endpoint `PATCH /api/auth/profile/student/update/` existe y que
`/api/auth/me/` (`api_profile`, vista `GET`) incluye el campo `student_profile`
en su respuesta. Si alguno de los dos no está implementado en la rama donde se
corren, los tests van a fallar — eso es información útil, no un bug del test.

---

## ⚠️ Notas

- Los usuarios generados con `generate_test_users` son reales en la base — no se
  borran solos. Usá `--clear` periódicamente o en CI antes de cada corrida.
- El comando es **idempotente respecto a colisiones de username**: si genera un
  nombre que ya existe, lo saltea silenciosamente y sigue con el resto.
- No usar `--role ADMIN` en bulk en un ambiente compartido sin avisar al equipo —
  los usuarios ADMIN tienen `is_staff=True` y acceso al panel de administración.
