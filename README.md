# Mentor Virtual Adaptativo — Backend + Frontend

Plataforma de acompañamiento educativo con IA para adultos con escolaridad incompleta en la Ciudad de Buenos Aires.

---

## 🎯 Visión y Objetivos

El **Mentor Virtual Adaptativo** ayuda a adultos que dejaron sus estudios a retomar el aprendizaje mediante planes personalizados generados con IA, videos seleccionados automáticamente, un tutor inteligente con RAG y mecánicas de gamificación para sostener la motivación.

### 💡 Propuesta de Valor
- **Planes adaptativos con IA:** El usuario escribe su meta en lenguaje libre y Claude API genera un plan personalizado con pasos graduales.
- **Videos reales por paso:** YouTube Data API v3 selecciona automáticamente el video más relevante para cada paso del plan.
- **Tutor RAG por paso:** El robot mentor responde preguntas basándose en libros PDF subidos por el usuario, usando embeddings con pgvector. Si no hay libro relevante, responde acotado al tema sin inventar.
- **Gamificación:** Sistema de logros desbloqueables, racha de días activos (streaks) y progreso visual por meta.
- **Robot con emociones:** El mentor tiene 8 estados emocionales (feliz, pensativo, ayudando, sorprendido, etc.) que cambian según el contexto.
- **Sistema de roles:** ADMIN, PROFESSOR y STUDENT con permisos diferenciados.
- **Perfil de accesibilidad:** Tamaño de tipografía, alto contraste y guía por voz configurables por usuario.
- **Diseño institucional:** Frontend alineado con Obelisco v2, el sistema de diseño oficial del GCBA.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Lenguaje backend | Python | 3.12 |
| Framework backend | Django + DRF | 5.x |
| Servidor WSGI | Gunicorn | 22.x |
| Autenticación | SimpleJWT | Access 2h / Refresh 30d |
| Base de datos | PostgreSQL + pgvector | 16 |
| Embeddings RAG | sentence-transformers | paraphrase-multilingual-MiniLM-L12-v2 |
| Extracción PDF | pdfplumber | 0.11+ |
| Deep Learning | PyTorch (CPU/CUDA) | 2.3+ |
| Framework frontend | React + TypeScript + Vite | 18.x / 5.x |
| Design system | Obelisco v2 (GCBA) | 1.11.1 |
| Proxy / Static | Nginx | 1.27 |
| Contenedores | Docker + Compose | v3.9 |
| IA generativa | Claude API (Anthropic) | configurable vía `AI_PROVIDER` (Anthropic, OpenAI, DeepSeek, Gemini, Ollama) |
| Videos | YouTube Data API v3 | Google |
| Documentación API | drf-spectacular | Swagger + ReDoc |
| Datos geográficos | API GeoRef (datos.gob.ar) | precarga vía `manage.py load_georef` |

---

## 🚀 Guía de Instalación

### 1. Clonar y configurar
```bash
git clone <repo>
cd MentorVirtual
cp .env.example .env
# Editá .env con tus claves reales (ver sección Variables de Entorno)
```

### 2. Crear la red Docker
```bash
docker network create mentor_net
```

### 3. Levantar servicios
```bash
docker compose up --build
```

Levanta tres servicios:
- `postgres` — PostgreSQL 16 con pgvector en el puerto `5432`
- `backend` — Django en el puerto `8000`
- `frontend` — Vite con HMR en el puerto `5173`

### 4. Inicializar la base de datos
```bash
# Extensión pgvector + tablas propias + stored procedures
docker exec -i mentor-postgres-1 psql -U postgres -d MentorVirtual < backend/init.sql

# Tablas de Django (auth, users, sessions, etc.)
docker compose exec backend python manage.py migrate

# Datos geográficos (países/provincias/localidades de Argentina, ~3.800 registros)
docker compose exec backend python manage.py load_georef
```

> ⚠️ **Ojo con el nombre de la base:** el valor de `POSTGRES_DB` en `.env`/`.env.example` tiene que coincidir EXACTO (mayúsculas incluidas) con el que usás en cada comando de `psql`/`migrate`. Es una fuente recurrente de errores confusos ("`database does not exist`") cuando alguien tipea `mentor_virtual` en un lugar y `MentorVirtual` en otro. Copiá y pegá el valor de tu `.env`, no lo escribas de memoria.
>
> `init.sql` **no se carga solo** al levantar el contenedor de Postgres — el mount en `docker-compose.yml` está comentado a propósito. Hay que correr el comando de arriba a mano cada vez que cambia (por ejemplo, después del fix de timezone en `sp_update_streak`, sección de Cambios Recientes).

### 5. Crear usuarios iniciales
Ver sección **Gestión de Usuarios** más abajo.

### 6. Verificar que todo funciona
- **Frontend:** http://localhost:5173
- **API Docs (Swagger):** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **Admin Django:** http://localhost:8000/admin/

---

## 👥 Gestión de Usuarios y Roles

El sistema tiene tres roles: `STUDENT` (default), `PROFESSOR` y `ADMIN`.

- **STUDENT** — puede crear metas, subir libros y ver su propio progreso.
- **PROFESSOR** — puede borrar metas y libros de cualquier usuario.
- **ADMIN** — igual que PROFESSOR más acceso al panel de administración.

### Crear superusuario (ADMIN)
```bash
docker compose exec backend python manage.py createsuperuser
```

### Crear usuario administrador desde shell
```bash
docker compose exec backend python manage.py shell -c "
from django.contrib.auth.models import User
u = User.objects.create_superuser('admin', 'admin@mentovirtual.com', 'Admin1234!')
print('Admin creado OK')
"
```

### Crear profesor
```bash
docker compose exec backend python manage.py shell -c "
from django.contrib.auth.models import User
u = User.objects.create_user('profe', 'profe@mentovirtual.com', 'Profe1234!')
u.profile.role = 'PROFESSOR'
u.profile.save()
print('Profesor creado OK')
"
```

### Crear alumno (usuario demo)
```bash
docker compose exec backend python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='demo').exists():
    User.objects.create_user('demo', 'demo@mentovirtual.com', 'Demo1234!')
    print('Demo creado OK')
else:
    print('Ya existe')
"
```

### Cambiar rol de un usuario existente
```bash
docker compose exec backend python manage.py shell -c "
from django.contrib.auth.models import User
u = User.objects.get(username='nombre_usuario')
u.profile.role = 'PROFESSOR'  # o 'ADMIN' o 'STUDENT'
u.profile.save()
print('Rol actualizado OK')
"
```

### Generar password seguro con Python
```bash
python3 -c "import secrets, string; chars = string.ascii_letters + string.digits + '!@#\$%'; print(''.join(secrets.choice(chars) for _ in range(16)))"
```

---

## 🔑 Variables de Entorno y APIs Externas

Copiá `.env.example` como `.env` y completá cada valor.

### Django
```bash
SECRET_KEY=          # Clave secreta. Generala con:
                     # python3 -c "import secrets; print(secrets.token_urlsafe(50))"
DEBUG=True           # False en producción
ALLOWED_HOSTS=localhost,127.0.0.1,TU_IP
```

### Base de datos PostgreSQL
```bash
POSTGRES_DB=MentorVirtual
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password_seguro
POSTGRES_HOST=postgres   # nombre del servicio Docker
POSTGRES_PORT=5432
```

### 🤖 Claude API (Anthropic) — Planes adaptativos con IA
**URL:** https://console.anthropic.com

1. Creá una cuenta en https://console.anthropic.com
2. Ir a **API Keys** → **Create Key**
3. Copiá la clave que empieza con `sk-ant-`

**Planes disponibles:**
- **Free:** $5 de crédito inicial para pruebas
- **Build:** pay-as-you-go desde $0.003 por 1K tokens (claude-sonnet)
- **Scale:** volumen con descuento

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
```

> El sistema usa `claude-sonnet-4-20250514` con `max_tokens=1024` para minimizar costos. Cada plan generado consume aproximadamente 800-1200 tokens de entrada y 400-600 de salida.

### 🎬 YouTube Data API v3 — Videos por paso
**URL:** https://console.cloud.google.com

1. Creá un proyecto en Google Cloud Console
2. Ir a **APIs y Servicios** → **Habilitar APIs** → buscar "YouTube Data API v3" → Habilitar
3. Ir a **Credenciales** → **Crear credenciales** → **Clave de API**
4. Recomendado: restringir la clave a YouTube Data API v3

**Cuota gratuita:** 10.000 unidades por día (cada búsqueda consume 100 unidades → ~100 búsquedas/día gratis)

```bash
YOUTUBE_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 🤗 HuggingFace — Descarga de modelos de embeddings
**URL:** https://huggingface.co/settings/tokens

1. Creá cuenta en https://huggingface.co
2. Ir a Settings → **Access Tokens** → **New token**
3. Tipo: **Read** (solo lectura es suficiente)

**Es gratuito.** Sin token funciona igual pero con rate limit más bajo al descargar el modelo por primera vez.

```bash
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx
```

### Frontend
```bash
VITE_APP_NAME=Mentor Virtual    # Nombre de la app mostrado en el frontend
VITE_MENTOR_NAME=Pulso          # Nombre del robot mentor
FRONTEND_URL=http://TU_IP:5173  # URL del frontend para redirect desde Django
```

### CORS
```bash
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://TU_IP:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://TU_IP:5173,http://TU_IP:8000
```

### Base de datos alternativa (si usás DATABASE_URL en lugar de variables separadas)
```bash
DATABASE_URL=postgresql://usuario:password@host:5432/nombre_db
```

---

## 📁 Estructura del Proyecto

```
MentorVirtual/
├── backend/
│   ├── MentorVirtual/      ← configuración global (settings, urls, wsgi)
│   ├── users/              ← registro, login, JWT, roles, perfil, accesibilidad, StudentProfile, geo (países/provincias/localidades)
│   │   ├── models.py       ← UserProfile + UserConfig + StudentProfile (campos en inglés) + Country/Province/Locality/Nationality + UserActivityLog
│   │   ├── views.py        ← login por email, register, profile GET/PUT/PATCH, rate limiting en login/register
│   │   ├── views_geo.py    ← endpoints de países/provincias/localidades
│   │   ├── management/commands/load_georef.py ← precarga de datos geográficos desde la API de GeoRef
│   │   └── serializers.py  ← validaciones OWASP, mensajes en español
│   ├── goals/               ← metas, planes IA, videos YouTube, delete por rol — SP-only (sin ORM, `connection.cursor()` directo)
│   ├── progress/            ← pasos completados, logros, streaks
│   ├── tutor/                ← RAG con PDF + embeddings + tutor por paso + chat libre con Pulso
│   ├── enrollment/          ← inscripciones a cursos (SP `sp_enroll_student`/`sp_get_my_enrollments`) + email de bienvenida asíncrono
│   ├── courses/              ← cursos/módulos/lecciones — fuera de scope MVP, congelado como backlog
│   ├── adminpanel/          ← panel de administración frontend
│   └── init.sql              ← tablas propias + stored procedures (fix de timezone en streaks incluido)
├── frontend/
│   ├── src/
│   │   ├── components/     ← MentorBot, Sidebar, MentorChat, TutorFloatingChat, GoalCard, landing/
│   │   ├── pages/          ← Landing, Dashboard, Login, GoalDetail, TutorPage, Profile, AdminPanel
│   │   └── services/       ← api.ts
│   └── vite.config.ts      ← proxy /api/ → Django
├── nginx/                  ← reverse proxy para producción
├── docker-compose.yml      ← desarrollo
└── docker-compose.prod.yml ← producción
```

---

## 📡 Endpoints de la API

> Todas las URLs abajo van después de `/api/`. Base local: `http://localhost:8000/api/...`

### Autenticación y perfil (`users`)
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| POST | `auth/register/` | No | Crear cuenta (validación OWASP). Rate limit: 3/min por IP |
| POST | `auth/login/` | No | Login por **email** → access + refresh JWT. Rate limit: 3/min por IP |
| POST | `auth/token/refresh/` | No | Renovar access token (rota el refresh también, `ROTATE_REFRESH_TOKENS=True`) |
| POST | `auth/logout/` | JWT | Invalida el refresh token |
| GET  | `auth/me/` | JWT | Perfil completo (rol, config de accesibilidad, datos de residencia geográfica) |
| PUT/PATCH | `auth/me/` | JWT | Actualizar email, teléfono, avatar, accesibilidad, país/provincia/localidad |
| POST | `auth/change_password/` | JWT | Cambiar contraseña (validación OWASP) |
| GET  | `auth/users/` | Staff | Listado paginado de usuarios |
| GET  | `auth/profile/student/update/` | JWT | Perfil de analítica del estudiante (ver campos abajo) |
| PATCH | `auth/profile/student/update/` | JWT | Actualizar perfil de estudiante — solo campos demográficos, los de analítica son de solo lectura |
| GET | `auth/geo/countries/` | JWT | Listado de países |
| GET | `auth/geo/provinces/list?country=<id>` | JWT | Provincias de un país |
| POST | `auth/geo/provinces/` | JWT | Buscar provincia por nombre libre (`{"name": "Córdoba"}`) |
| GET | `auth/geo/localities/?province=<id>` | JWT | Localidades de una provincia (`province` es obligatorio) |

**Campos de `StudentProfile` — migrados de español a inglés esta sesión:**

| Campo (actual, inglés) | Editable por el usuario | Nota |
|---|:---:|---|
| `birth_date` | ✅ | |
| `education_level` | ✅ | choices en español (`primario_completo`, etc.) — son datos, no nombres de variable |
| `employment_status` | ✅ | |
| `user_gender` | ✅ | |
| `primary_objective` | ✅ | |
| `time_availability` | ✅ | |
| `time_zone` | ✅ | default `America/Argentina/Buenos_Aires` |
| `user_interests` | ✅ | array de strings |
| `entry_frequency`, `current_streak_days`, `max_streak_days`, `app_time_min`, `mentor_interaction_time_min`, `watched_videos_count`, `youtube_api_time_min`, `completed_challenges` | ❌ solo lectura | los actualiza el sistema, un PATCH sobre estos campos se ignora en silencio (200 OK sin cambios) |
| `last_connection` | ❌ solo lectura | ya estaba en inglés antes de esta migración |

### Metas y Planes (`goals`) — SP-only, sin ORM
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET    | `goals/` | JWT | Listar metas del usuario |
| POST   | `goals/create/` | JWT | Crear meta → genera plan con IA + videos |
| GET    | `goals/<id>/` | JWT | Detalle: pasos + videos + logros |
| DELETE | `goals/<id>/delete/` | JWT | Eliminar meta (PROFESSOR/ADMIN: cualquier meta) |

### Progreso (`progress`)
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| POST | `progress/steps/<id>/complete/` | JWT | Completar un paso |
| POST | `progress/videos/<id>/view/` | JWT | Registrar video visto |
| GET  | `progress/goals/<id>/` | JWT | Progreso de una meta |
| GET  | `progress/streak/` | JWT | Racha de días activos (fix de timezone Buenos Aires aplicado en `sp_update_streak`) |
| GET  | `progress/logros/` | JWT | Logros del usuario |

### Tutor RAG (`tutor`)
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET    | `tutor/books/` | JWT | Listar libros subidos |
| POST   | `tutor/books/` | JWT | Subir y procesar PDF |
| DELETE | `tutor/books/<id>/` | JWT | Eliminar libro (PROFESSOR/ADMIN: cualquier libro) |
| POST   | `tutor/books/<id>/ask/` | JWT | Preguntar sobre un libro específico |
| POST   | `tutor/ask_step/` | JWT | Robot tutor por paso (busca en todos los libros del usuario) |
| POST   | `tutor/chat/` | JWT | Chat libre con Pulso — busca en libros y transcripciones de clases antes de responder con IA |

### Panel de Administración (`adminpanel`)
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET   | `admin/users/` | Staff | Listar usuarios |
| GET   | `admin/users/<id>/` | Staff | Detalle de usuario |
| PATCH | `admin/users/<id>/` | Staff | Activar/desactivar usuario |
| POST  | `admin/users/<id>/set_password/` | Staff | Cambiar contraseña de usuario |
| GET   | `admin/stats/` | Staff | Estadísticas generales |
| POST  | `admin/users/create-professor/` | Staff | Alta de cuenta de profesor |

### Inscripciones (`enrollment`)
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET  | `enrollment/courses/available/` | JWT | Cursos disponibles para inscripción |
| POST | `enrollment/enroll/` | STUDENT | Inscribirse a un curso — dispara email de bienvenida asíncrono |
| GET  | `enrollment/enrollments/list/` | ADMIN/PROFESSOR | Listado completo de inscripciones |
| GET  | `enrollment/enrollments/my-courses/` | STUDENT | Cursos propios del alumno autenticado |

### Cursos (`courses`) — ⚠️ fuera de scope para Demo Day
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET/POST | `courses/` | JWT | Listar (Admin: todos, Profesor: el suyo) / crear curso manual |
| POST | `courses/generate-with-ai/` | JWT | Generar curso con IA |
| GET/PATCH/DELETE | `courses/<id>/` | JWT | Detalle / editar / borrar curso |
| GET/POST | `courses/<id>/modules/` | JWT | Módulos de un curso |
| GET/PATCH | `courses/modules/<id>/` | JWT | Detalle / editar módulo |
| GET/POST | `courses/modules/<id>/lessons/` | JWT | Lecciones de un módulo |
| GET/PATCH | `courses/lessons/<id>/` | JWT | Detalle / editar lección |
| POST | `courses/lessons/<id>/complete-rate/` | JWT | Completar y calificar lección |
| GET | `courses/modules/<id>/quiz/` | JWT | Cuestionario de un módulo |
| POST | `courses/modules/<id>/quiz-submit/` | JWT | Enviar respuestas del cuestionario |
| GET | `courses/<id>/student-state/` | JWT | Estado de progreso del alumno en el curso |
| GET | `courses/alerts/inactivity/` | JWT | Alertas de inactividad |

> Este módulo está documentado porque existe en el código, pero es **scope creep sin mandato formal** — congelado como backlog post-Demo Day. No es prioridad de testing hasta que se confirme oficialmente.

### Documentación
| URL | Descripción |
|-----|-------------|
| `/api/docs/` | Portal de documentación centralizado |
| `/api/schema/swagger-ui/` | Swagger UI interactivo |
| `/api/schema/redoc/` | ReDoc |
| `/api/schema/` | Schema OpenAPI JSON/YAML |

---

## 🗺️ Mapa rápido para QA (dónde probar en Swagger)

Abrí `/api/schema/swagger-ui/` y ubicá cada bloque por su tag:

| Tag en Swagger | Qué cubre | Prioridad de testing |
|---|---|:---:|
| **auth** | Registro, login, logout, refresh, cambio de password, perfil (`/me/`) | 🔴 Alta — MVP core |
| **auth** (sub-bloque perfil estudiante) | `profile/student/update/` — ver tabla de campos arriba antes de armar payloads | 🔴 Alta — recién migrado a inglés, validar que no queden referencias viejas |
| **auth** (sub-bloque geo) | `geo/countries/`, `geo/provinces/`, `geo/localities/` | 🟡 Media — soporte de registro/perfil, no bloquea flujo principal |
| **goals** | Metas y planes con IA | 🔴 Alta — MVP core |
| **progress** | Pasos, videos, streak, logros | 🔴 Alta — MVP core (racha con fix de timezone reciente, vale la pena re-testear puntualmente) |
| **tutor** | Libros, preguntas, chat con Pulso | 🔴 Alta — MVP core |
| **enrollment** | Inscripción a cursos + email de confirmación | 🟡 Media — funcional, pero depende de `courses` para tener datos de prueba |
| **courses** | CRUD de cursos, módulos, lecciones, quizzes | ⚪ Baja / fuera de scope — no es prioridad, congelado para Demo Day |
| **admin** | Panel de administración | 🟡 Media — requiere usuario `is_staff` |

**Para armar un usuario de prueba con permisos de Staff/Admin** (necesario para `admin/*` y para probar `courses` si igual quieren cubrirlo):
```bash
docker compose exec backend python manage.py createsuperuser
```

**Cambios de esta sesión que ameritan re-test puntual:**
- Todo `auth/profile/student/update/` — nombres de campo cambiaron de español a inglés (ver tabla arriba). Cualquier colección de Postman/request guardado con los nombres viejos (`fecha_nacimiento`, `nivel_educativo`, etc.) va a fallar en silencio (DRF ignora keys no reconocidas, no tira error).
- `auth/logout/` — ahora también registra el evento en la tabla de auditoría (antes no se estaba guardando el timestamp de logout).
- `progress/streak/` — fix de zona horaria en el cálculo de "qué día es hoy" (antes usaba el timezone del servidor de Postgres, que por default es UTC).

---

## 🗄️ Modelo de Datos

### Tablas gestionadas por Django (ORM + migraciones)
| Tabla | Descripción |
|-------|-------------|
| `auth_user` | Usuarios del sistema |
| `users_userprofile` | Perfil extendido: role, phone, avatar_url, bio_face_hash, residencia geográfica |
| `users_userconfig` | Accesibilidad: font_size, high_contrast, voice_guidance |
| `users_studentprofile` | Analítica de estudiante — campos en inglés (ver tabla en Endpoints) |
| `users_professorprofile` | Datos de docentes |
| `users_country` / `users_province` / `users_locality` / `users_nationality` | Catálogo geográfico normalizado, precargado desde la API de GeoRef |
| `users_useractivitylog` | Auditoría de eventos (login, logout, etc.) con timestamp |
| `enrollment_*` | Migraciones propias de Django para el módulo de inscripciones (la lógica de negocio corre por stored procedure, ver abajo) |

### Tablas propias (stored procedures, sin ORM)
| Tabla | Descripción |
|-------|-------------|
| `goals` | Metas en lenguaje libre |
| `steps` | Pasos del plan generado por IA |
| `videos` | Videos de YouTube por paso |
| `logros` | Badges desbloqueables |
| `user_progress` | Pasos completados por usuario |
| `video_views` | Videos vistos por usuario |
| `streaks` | Racha de días activos |
| `tutor_books` | Libros PDF subidos |
| `tutor_chunks` | Fragmentos del PDF con embeddings vector(384) |

> Las stored procedures de `enrollment` (`sp_enroll_student`, `sp_get_my_enrollments`) viven junto a las migraciones de esa app, no en `init.sql` — se cargan solas al correr `migrate`.

---

## 🤖 Arquitectura RAG (Tutor con libros PDF)

```
PDF subido por el usuario
    │
    ▼
pdfplumber extrae texto por página
    │
    ▼
Fragmentación en chunks de ~500 chars
    │
    ▼
sentence-transformers genera embeddings (384 dims)
    │   modelo: paraphrase-multilingual-MiniLM-L12-v2
    │   dispositivo: CUDA si disponible, CPU si no
    │
    ▼
Guardado en PostgreSQL con pgvector (índice ivfflat cosine)
    │
    ▼
Usuario pregunta en un paso del plan
    │
    ▼
Django busca los 2 chunks más similares (cosine similarity)
    │
    ├── similitud > 0.4 → responde con RAG (grounded en el libro)
    │
    └── similitud < 0.4 → responde acotado al tema del paso (sin inventar)
```

> **Nota:** PDFs escaneados (imágenes) no son procesables con pdfplumber. Solo funcionan PDFs de texto. Soporte OCR (Tesseract) está en el roadmap.

---

## 🎮 Sistema de Gamificación

- **Logros:** Se desbloquean automáticamente al 25%, 60% y 100% de pasos completados.
- **Streaks:** Racha de días consecutivos con actividad. Se actualiza al completar pasos o ver videos.
- **Progreso visual:** Barra de progreso por meta con porcentaje.
- **Robot con emociones:** 8 estados (feliz, emocionado, pensativo, guiñando, ayudando, sorprendido, triste, enamorado).

---

## 🔐 Sistema de Roles

| Rol | Crear metas | Subir libros | Borrar metas propias | Borrar cualquier meta/libro | Panel admin |
|-----|:-----------:|:------------:|:--------------------:|:---------------------------:|:-----------:|
| STUDENT   | ✅ | ✅ | ✅ | ❌ | ❌ |
| PROFESSOR | ✅ | ✅ | ✅ | ✅ | ❌ |
| ADMIN     | ✅ | ✅ | ✅ | ✅ | ✅ |

Los usuarios `is_staff` o `is_superuser` de Django son automáticamente rol ADMIN.

---

## ✅ Testing

Backend con `pytest` + `pytest-django`:

```bash
docker compose exec backend pytest
```

Config en `backend/pytest.ini` (`DJANGO_SETTINGS_MODULE`, detección de `tests.py`, clases `*TestCase`, funciones `test_*`). Las llamadas a proveedores de IA se mockean con `monkeypatch`, no pegan a la API real en los tests.

No hay suite de testing de frontend todavía.

---

## 🐳 Producción

```bash
# Build del frontend
cd frontend && npm run build && cd ..

# Levantar Django (Gunicorn) + Nginx
docker compose -f docker-compose.prod.yml up --build -d
```

Nginx sirve el React build estático y hace reverse proxy a `/api/` y `/admin/` hacia Gunicorn.

---

## 📋 Roadmap

### ✅ MVP — Completado
- Registro y login por email con JWT + validaciones OWASP + rate limiting (3/min)
- Perfil de usuario con accesibilidad (font_size, high_contrast, voice_guidance)
- Sistema de roles (ADMIN, PROFESSOR, STUDENT)
- Planes adaptativos con IA (abstracción multi-proveedor: Anthropic, OpenAI, DeepSeek, Gemini, Ollama)
- Videos automáticos con YouTube API
- Sistema de logros y streaks (timezone Buenos Aires)
- Tutor RAG con PDF y pgvector + chat libre con Pulso
- Robot con 8 estados emocionales
- Panel admin frontend
- Eliminar metas y libros con control de roles
- Cambio de contraseña desde el perfil
- Datos geográficos normalizados (países/provincias/localidades) para perfil de usuario
- Notificaciones por email (bienvenida al registrarse, confirmación al inscribirse a un curso)
- Registro de actividad de usuario (login/logout, con timestamp)
- Documentación Swagger + ReDoc + portal propio
- Deploy con Docker (dev y prod)

> **Scope de Demo Day (bloqueado):** Feed, contenido, desafíos, streaks/logros, chat con el mentor. El módulo `courses` (roles ADMIN/PROFESSOR/STUDENT completo, generación de cursos con IA, integración biométrica/RENAPER) es scope creep sin mandato formal del brief original — queda documentado y funcional en el código, pero congelado como backlog post-demo.

### 🔜 Fase 2 — En planificación
- Rutas de carrera por área y nivel (Tecnología, Oficios, Administración, etc.)
- Múltiples métodos de autenticación:
  - Biometría facial (Face-api.js — campo `bio_face_hash` ya reservado en UserProfile)
  - Magic link / OTP por email
  - OTP por WhatsApp (Meta Cloud API — gratis hasta 1.000 conv/mes)
- OCR para PDFs escaneados (Tesseract)
- GPU support en Docker (NVIDIA Container Toolkit)
- Integración completa Obelisco v2
- SSO con cuenta de Buenos Aires (GCBA)
- Persistencia de quiz en backend (hoy vive en localStorage del frontend)
- Rotación de `SECRET_KEY` (sigue con el valor `django-insecure-` de template)

---

## 🧾 Cambios recientes (esta sesión)

- **`StudentProfile` migrado de español a inglés**: 16 campos renombrados (`fecha_nacimiento`→`birth_date`, `nivel_educativo`→`education_level`, etc. — tabla completa en la sección de Endpoints). Migración de base de datos vía `RenameField` (no destructiva, preserva los datos existentes de usuarios reales).
- **Rate limiting** en `auth/login/` y `auth/register/` (3 intentos por minuto por IP).
- **Logging estructurado**: consola + archivo persistente `errors.log`, separado por app (`django`, `users`, `enrollment`).
- **Notificaciones por email** (asíncronas, no bloquean la respuesta HTTP): bienvenida al registrarse, confirmación al inscribirse a un curso.
- **Fix de timezone en streaks**: `sp_update_streak` calculaba "qué día es hoy" según el timezone del servidor de Postgres (UTC por default), rompiendo la racha para usuarios que completaban algo entre las 21:00 y las 23:59 hora Argentina. Ahora se fija explícitamente `America/Argentina/Buenos_Aires` en la propia stored procedure.
- **Fix de logout incompleto**: el frontend limpiaba el `localStorage` pero nunca llamaba al endpoint `/api/auth/logout/` — el evento de logout no quedaba registrado en la auditoría (`UserActivityLog`). Corregido en `App.tsx`/`api.ts`.
- **Landing page pública** integrada como pantalla previa al login/registro.

---
