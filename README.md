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
| IA generativa | Claude API (Anthropic) | claude-sonnet-4-20250514 |
| Videos | YouTube Data API v3 | Google |
| Documentación API | drf-spectacular | Swagger + ReDoc |

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
```

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
│   ├── users/              ← registro, login, JWT, roles, perfil, accesibilidad
│   │   ├── models.py       ← UserProfile (role, bio_face_hash) + UserConfig (accesibilidad)
│   │   ├── views.py        ← login por email, register, profile GET/PUT/PATCH
│   │   └── serializers.py  ← validaciones OWASP, mensajes en español
│   ├── goals/              ← metas, planes IA, videos YouTube, delete por rol
│   ├── progress/           ← pasos completados, logros, streaks
│   ├── tutor/              ← RAG con PDF + embeddings + tutor por paso
│   ├── adminpanel/         ← panel de administración frontend
│   └── init.sql            ← tablas propias + stored procedures (incluye fix id ambiguo)
├── frontend/
│   ├── src/
│   │   ├── components/     ← MentorBot, Sidebar, MentorChat, TutorFloatingChat, GoalCard
│   │   ├── pages/          ← Dashboard, Login, GoalDetail, TutorPage, Profile, AdminPanel
│   │   └── services/       ← api.ts
│   └── vite.config.ts      ← proxy /api/ → Django
├── nginx/                  ← reverse proxy para producción
├── docker-compose.yml      ← desarrollo
└── docker-compose.prod.yml ← producción
```

---

## 📡 Endpoints de la API

### Autenticación
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| POST | `/api/auth/register/` | No | Crear cuenta (validación OWASP) |
| POST | `/api/auth/login/` | No | Login por **email** → access + refresh JWT |
| POST | `/api/auth/token/refresh/` | No | Renovar access token |
| POST | `/api/auth/logout/` | JWT | Invalidar refresh token |
| GET  | `/api/auth/me/` | JWT | Perfil completo con rol y config de accesibilidad |
| PUT/PATCH | `/api/auth/me/` | JWT | Actualizar email, teléfono, avatar, accesibilidad |
| POST | `/api/auth/change_password/` | JWT | Cambiar contraseña (validación OWASP) |
| GET  | `/api/auth/users/` | Staff | Listado paginado de usuarios |

### Metas y Planes
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET    | `/api/goals/` | JWT | Listar metas del usuario |
| POST   | `/api/goals/create/` | JWT | Crear meta → genera plan con IA + videos |
| GET    | `/api/goals/<id>/` | JWT | Detalle: pasos + videos + logros |
| DELETE | `/api/goals/<id>/delete/` | JWT | Eliminar meta (PROFESSOR/ADMIN: cualquier meta) |

### Progreso
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| POST | `/api/progress/steps/<id>/complete/` | JWT | Completar un paso |
| POST | `/api/progress/videos/<id>/view/` | JWT | Registrar video visto |
| GET  | `/api/progress/goals/<id>/` | JWT | Progreso de una meta |
| GET  | `/api/progress/streak/` | JWT | Racha de días activos |
| GET  | `/api/progress/logros/` | JWT | Logros del usuario |

### Tutor RAG
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET    | `/api/tutor/books/` | JWT | Listar libros subidos |
| POST   | `/api/tutor/books/` | JWT | Subir y procesar PDF |
| DELETE | `/api/tutor/books/<id>/` | JWT | Eliminar libro (PROFESSOR/ADMIN: cualquier libro) |
| POST   | `/api/tutor/books/<id>/ask/` | JWT | Preguntar sobre un libro específico |
| POST   | `/api/tutor/ask_step/` | JWT | Robot tutor por paso (busca en todos los libros) |

### Panel de Administración
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET   | `/api/admin/users/` | Staff | Listar usuarios |
| GET   | `/api/admin/users/<id>/` | Staff | Detalle de usuario |
| PATCH | `/api/admin/users/<id>/` | Staff | Activar/desactivar usuario |
| POST  | `/api/admin/users/<id>/set_password/` | Staff | Cambiar contraseña de usuario |
| GET   | `/api/admin/stats/` | Staff | Estadísticas generales |

### Documentación
| URL | Descripción |
|-----|-------------|
| `/api/docs/` | Portal de documentación centralizado |
| `/api/schema/swagger-ui/` | Swagger UI interactivo |
| `/api/schema/redoc/` | ReDoc |
| `/api/schema/` | Schema OpenAPI JSON/YAML |

---

## 🗄️ Modelo de Datos

### Tablas gestionadas por Django (ORM + migraciones)
| Tabla | Descripción |
|-------|-------------|
| `auth_user` | Usuarios del sistema |
| `users_userprofile` | Perfil extendido: role, phone, avatar_url, bio_face_hash |
| `users_userconfig` | Accesibilidad: font_size, high_contrast, voice_guidance |

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
- Registro y login por email con JWT + validaciones OWASP
- Perfil de usuario con accesibilidad (font_size, high_contrast, voice_guidance)
- Sistema de roles (ADMIN, PROFESSOR, STUDENT)
- Planes adaptativos con Claude API
- Videos automáticos con YouTube API
- Sistema de logros y streaks
- Tutor RAG con PDF y pgvector
- Robot con 8 estados emocionales
- Panel admin frontend
- Eliminar metas y libros con control de roles
- Cambio de contraseña desde el perfil
- Documentación Swagger + ReDoc + portal propio
- Deploy con Docker (dev y prod)

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
