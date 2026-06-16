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
docker compose exec backend python manage.py test users --verbosity=2
```

### Opción 2 — Reporte HTML visual (recomendado para QA)

```bash
# Instalar dependencias (solo la primera vez)
docker compose exec backend pip install pytest pytest-django pytest-html

# Crear carpeta de reportes en el host
mkdir -p test-reports

# Correr y generar reporte HTML
docker compose exec backend pytest users/tests.py \
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
17 passed in X.XXXs
```

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

---

## Notas importantes para QA

- **Autenticación:** JWT Bearer token — NO Token DRF
- **Login:** siempre por **EMAIL**, no por username
- **Base de datos de tests:** Django crea una DB temporal separada que se destruye al terminar — no afecta la DB de desarrollo
- **Modelos:** `auth.User` + `UserProfile` (OneToOne) + `UserConfig` (OneToOne), creados automáticamente por señales Django al registrar un usuario
- **Roles:** STUDENT (default), PROFESSOR, ADMIN — el usuario de prueba tiene `is_staff=True` para poder testear el listado de usuarios
