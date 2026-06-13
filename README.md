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
cd mentor_virtual
cp .env.example .env
# Editá .env con tus claves reales
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
# Tablas propias + stored procedures
docker exec -i mentor-postgres-1 psql -U postgres -d mentor_virtual < backend/init.sql

# Tablas de Django (auth, sessions, etc.)
docker compose exec backend python manage.py migrate
```

### 5. Crear superusuario
```bash
docker compose exec backend python manage.py createsuperuser
```

### 6. Verificar que todo funciona
- **Frontend:** http://localhost:5173
- **API Docs (Swagger):** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **Admin Django:** http://localhost:8000/admin/
- **Admin Frontend:** login con usuario staff → botón "Panel admin" en el sidebar

---

## 📁 Estructura del Proyecto

```
mentor_virtual/
├── backend/
│   ├── mentor_virtual/     ← configuración global (settings, urls, wsgi)
│   ├── users/              ← registro, login, JWT, cambio de contraseña
│   ├── goals/              ← metas, planes IA, videos YouTube
│   ├── progress/           ← pasos completados, logros, streaks
│   ├── tutor/              ← RAG con PDF + embeddings + tutor por paso
│   ├── adminpanel/         ← panel de administración frontend
│   └── init.sql            ← tablas propias + stored procedures
├── frontend/
│   ├── src/
│   │   ├── components/     ← MentorBot, Sidebar, MentorChat, TutorFloatingChat...
│   │   ├── pages/          ← Dashboard, Login, GoalDetail, TutorPage, Profile, AdminPanel
│   │   └── services/       ← api.ts (capa de comunicación con el backend)
│   └── vite.config.ts      ← proxy a /api/ → Django
├── nginx/                  ← reverse proxy para producción
├── docker-compose.yml      ← desarrollo
└── docker-compose.prod.yml ← producción
```

---

## 📡 Endpoints de la API

### Autenticación
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| POST | `/api/auth/register/` | No | Crear cuenta |
| POST | `/api/auth/login/` | No | Login → access + refresh token |
| POST | `/api/auth/token/refresh/` | No | Renovar access token |
| POST | `/api/auth/logout/` | JWT | Cerrar sesión |
| GET  | `/api/auth/me/` | JWT | Datos del usuario actual |
| POST | `/api/auth/change_password/` | JWT | Cambiar contraseña |

### Metas y Planes
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET  | `/api/goals/` | JWT | Listar metas del usuario |
| POST | `/api/goals/create/` | JWT | Crear meta → genera plan con IA + videos |
| GET  | `/api/goals/<id>/` | JWT | Detalle: pasos + videos + logros |

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
| GET  | `/api/tutor/books/` | JWT | Listar libros subidos |
| POST | `/api/tutor/books/` | JWT | Subir y procesar PDF |
| DELETE | `/api/tutor/books/<id>/` | JWT | Eliminar libro |
| POST | `/api/tutor/books/<id>/ask/` | JWT | Preguntar sobre un libro |
| POST | `/api/tutor/ask_step/` | JWT | Robot tutor por paso (busca en todos los libros) |

### Panel de Administración
| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET  | `/api/admin/users/` | Staff | Listar usuarios |
| GET  | `/api/admin/users/<id>/` | Staff | Detalle de usuario |
| PATCH | `/api/admin/users/<id>/` | Staff | Activar/desactivar usuario |
| POST | `/api/admin/users/<id>/set_password/` | Staff | Cambiar contraseña de usuario |
| GET  | `/api/admin/stats/` | Staff | Estadísticas generales |

### Documentación
| URL | Descripción |
|-----|-------------|
| `/api/docs/` | Swagger UI interactivo |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | Schema OpenAPI JSON/YAML |

---

## 🗄️ Modelo de Datos

### Tablas gestionadas por Django (ORM)
- `auth_user` — usuarios del sistema

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
Guardado en PostgreSQL con pgvector
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

---

## 🎮 Sistema de Gamificación

- **Logros:** Se desbloquean automáticamente al 25%, 60% y 100% de pasos completados.
- **Streaks:** Racha de días consecutivos con actividad. Se actualiza al completar pasos o ver videos.
- **Progreso visual:** Barra de progreso por meta con porcentaje.
- **Robot con emociones:** 8 estados (feliz, emocionado, pensativo, guiñando, ayudando, sorprendido, triste, enamorado) que cambian según el contexto.

---

## 🔒 Variables de Entorno

```bash
# Django
SECRET_KEY=django-insecure-cambia-esto
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,TU_IP

# PostgreSQL
POSTGRES_DB=mentor_virtual
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# APIs externas
ANTHROPIC_API_KEY=sk-ant-xxxxx
YOUTUBE_API_KEY=AIzaxxxxx

# HuggingFace (opcional, para mayor rate limit al bajar modelos)
HF_TOKEN=hf_xxxxx

# Frontend
VITE_APP_NAME=Mentor Virtual
VITE_MENTOR_NAME=Pulso
FRONTEND_URL=http://TU_IP:5173

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://TU_IP:5173
```

---

## 🐳 Producción

```bash
# Build del frontend
cd frontend && npm run build && cd ..

# Levantar Django + Nginx
docker compose -f docker-compose.prod.yml up --build -d
```

Nginx sirve el React build estático y hace reverse proxy a `/api/` y `/admin/` hacia Gunicorn.

---

## 📋 Roadmap

### ✅ MVP — Completado
- Registro y login con JWT
- Planes adaptativos con Claude API
- Videos automáticos con YouTube API
- Sistema de logros y streaks
- Tutor RAG con PDF y pgvector
- Robot con 8 estados emocionales
- Panel admin frontend
- Cambio de contraseña desde el perfil
- Documentación Swagger + ReDoc
- Deploy con Docker (dev y prod)

### 🔜 Fase 2 — En planificación
- Rutas de carrera por área y nivel (Tecnología, Oficios, Administración, etc.)
- Múltiples métodos de autenticación:
  - Biometría facial (Face-api.js, embeddings locales)
  - Magic link / OTP por email
  - OTP por WhatsApp (Meta Cloud API)
- OCR para PDFs escaneados (Tesseract)
- GPU support en Docker (NVIDIA Container Toolkit)
