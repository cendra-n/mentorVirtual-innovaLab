# Guía de Testing — Mentor Virtual

## Requisitos previos

El backend tiene que estar corriendo:

```bash
docker compose up backend postgres
```

---

## Correr los tests

### Opción 1 — Tests rápidos en consola (sin instalar nada)

```bash
# Solo users
docker compose exec backend python manage.py test users --verbosity=2

# Todo el backend (users + enrollment + courses)
docker compose exec backend python manage.py test --verbosity=2
```

### Opción 2 — Reporte HTML visual (recomendado para QA)

```bash
# Instalar dependencias (solo la primera vez)
docker compose exec backend pip install pytest pytest-django pytest-html

# Crear carpeta de reportes en el host
mkdir -p test-reports

# Correr y generar reporte HTML (todo el backend)
docker compose exec backend pytest \
  --html=/app/test-reports/report.html \
  --self-contained-html \
  -v

# Copiar reporte al host
docker cp equipo-1-mentor-virtual-2026-backend-1:/app/test-reports/report.html ./test-reports/
```

Abrís `test-reports/report.html` en el browser.

### Opción 3 — Reporte TXT (para adjuntar en tickets)

```bash
mkdir -p test-reports
docker compose exec backend python manage.py test users --verbosity=2 2>&1 | tee test-reports/report.txt
```

---

## Resultado esperado

```
30 passed in X.XXXs
```

(26 de `users` + 4 de `enrollment`. `courses` tiene su propia suite de 20 tests, pero ese módulo está fuera de scope para Demo Day — ver nota al final.)

---

## Tests disponibles

| # | Test | Qué valida |
|---|------|------------|
| 1 | `test_api_register_success` | Registro exitoso con todos los campos opcionales |
| 2 | `test_api_register_password_mismatch` | Contraseñas que no coinciden → 400 |
| 3 | `test_api_register_weak_password` | Contraseña débil sin mayúscula/número/especial → 400 |
| 4 | `test_api_register_duplicate_email` | Email ya registrado → 400 |
| 5 | `test_api_register_missing_fields` | Campos obligatorios vacíos → 400 |
| 6 | `test_api_register_invalid_phone` | Teléfono con formato inválido → 400 |
| 7 | `test_api_register_invalid_font_size` | font_size con valor no permitido → 400 |
| 8 | `test_api_login_success` | Login exitoso por email → JWT |
| 9 | `test_api_login_invalid_credentials` | Contraseña incorrecta → 400 |
| 10 | `test_api_login_missing_fields` | Campos de login vacíos → 400 |
| 11 | `test_api_profile_unauthorized` | Perfil sin token → 401 |
| 12 | `test_api_profile_get_success` | GET del perfil con token válido → 200 |
| 13 | `test_api_profile_update_put_success` | PUT actualiza perfil completo → 200 |
| 14 | `test_api_profile_update_patch_success` | PATCH actualiza campo parcial, resto sin cambios → 200 |
| 15 | `test_api_profile_update_duplicate_email_blocked` | Email duplicado en update → 400 |
| 16 | `test_api_users_list_success` | Listado paginado solo para staff → 200 |
| 17 | `test_api_logout_success` | Logout invalida refresh token → 200 |
| 18 | `test_api_update_student_profile_success` | PATCH actualiza campos demográficos de `StudentProfile` (nombres en inglés) → 200 |
| 19 | `test_api_update_student_profile_unauthorized` | Perfil de estudiante sin token → 401 |
| 20 | `test_api_update_student_profile_read_only_fields` | Campos de analítica (rachas, tiempo, videos vistos) ignoran cualquier intento de escritura externa |
| 21 | `test_api_login_creates_activity_log_and_online_status` | Login exitoso registra `UserActivityLog` tipo LOGIN y marca `session_status='ONLINE'` |
| 22 | `test_api_logout_creates_activity_log_and_offline_status` | Logout registra `UserActivityLog` tipo LOGOUT y marca `session_status='OFFLINE'` |
| 23 | `test_api_login_rate_limited_after_3_attempts` | 4to intento de login en el mismo minuto → 429 |
| 24 | `test_api_register_rate_limited_after_3_attempts` | 4to intento de registro en el mismo minuto → 429 |
| 25 | `test_login_and_register_throttles_are_independent` | Login y registro tienen baldes de rate-limit independientes (no se agotan entre sí) |
| 26 | `test_api_register_sends_welcome_email` | Registro exitoso encola un email de bienvenida al usuario nuevo |

---

## Tests de `enrollment` (inscripciones a cursos)

```bash
docker compose exec backend python manage.py test enrollment --verbosity=2
```

| # | Test | Qué valida |
|---|------|------------|
| 1 | `test_get_my_enrollments_as_student` | Un estudiante puede ver sus propias inscripciones → 200 |
| 2 | `test_get_my_enrollments_as_admin_forbidden` | Un admin NO puede usar el endpoint de "mis cursos" (es solo de alumno) → 403 |
| 3 | `test_unauthenticated_access` | Sin token → 401 |
| 4 | `test_reenroll_same_course_is_rejected_not_overwritten` | Inscribirse dos veces al mismo curso no pisa la inscripción existente → 400, y no crea una fila duplicada en `enrollment_enrollment` |

> El endpoint de inscripción (`POST /enrollment/enroll/`) también dispara un email de confirmación asíncrono al inscribirse — no tiene test dedicado todavía porque depende de `courses.models.Course`, que está fuera de scope. Si se prioriza, es el mismo patrón que `test_api_register_sends_welcome_email` (parchear `threading.Thread` con `ImmediateThread` + `mail.outbox`).

---

## Nota sobre `courses`

El módulo `courses` (CRUD de cursos/módulos/lecciones/quizzes, generación con IA) tiene su propia suite (`courses/tests.py`, 20 tests) y corre igual con `manage.py test courses`. No está detallado acá porque es **scope creep sin mandato formal** — congelado como backlog post-Demo Day. No es prioridad de testing hasta que se confirme oficialmente con el equipo de producto.

---

## Notas importantes para QA

- **Autenticación:** JWT Bearer token — NO Token DRF
- **Login:** siempre por **EMAIL**, no por username
- **Base de datos de tests:** Django crea una DB temporal separada que se destruye al terminar — no afecta la DB de desarrollo
- **Modelos:** `auth.User` + `UserProfile` (OneToOne) + `UserConfig` (OneToOne) + `StudentProfile` (OneToOne), creados automáticamente por señales Django al registrar un usuario
- **Roles:** STUDENT (default), PROFESSOR, ADMIN — el usuario de prueba tiene `is_staff=True` para poder testear el listado de usuarios
- **Rate limiting:** login y registro están limitados a 3 intentos por minuto por IP, cada uno con su propio balde independiente. Si estás probando a mano contra el mismo ambiente (no contra la suite de tests, que resetea el cache en cada test), y pegás varias veces seguidas, vas a chocar contra el 429 — es esperado, no un bug.
- **Auditoría de sesión:** cada login/logout exitoso queda registrado en `UserActivityLog` con timestamp (zona horaria Buenos Aires) — útil para verificar en base si un usuario de prueba realmente se logueó/deslogueó.
- **Emails:** en desarrollo, `EMAIL_BACKEND` por default es la consola (no manda emails reales) salvo que el `.env` tenga configurado SMTP real. Los tests fuerzan `locmem` explícitamente para no depender de esto.
