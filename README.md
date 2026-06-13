# Mentor Virtual Adaptativo

## Estructura del proyecto

```
mentor_virtual/
├── backend/          ← Django + DRF
│   ├── mentor_virtual/
│   ├── users/
│   ├── goals/
│   ├── progress/
│   ├── init.sql
│   ├── Dockerfile           (producción)
│   └── Dockerfile.dev       (desarrollo)
├── frontend/         ← React + TypeScript + Vite
│   ├── src/
│   ├── vite.config.ts
│   ├── Dockerfile           (build prod multi-stage)
│   └── Dockerfile.dev       (dev server con HMR)
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml        ← DESARROLLO
├── docker-compose.prod.yml   ← PRODUCCIÓN
└── .env.example
```

---

## Levantar en DESARROLLO

```bash
# 1. Variables de entorno
cp .env.example .env

# 2. Levantar todo (Django + Vite + Postgres)
docker compose up --build

# 3. En otra terminal: cargar tablas propias + stored procedures
docker compose exec postgres psql -U postgres -d mentor_virtual -f /docker-entrypoint-initdb.d/01_init.sql
#    (si el postgres ya corrió el init.sql automáticamente, salteá este paso)

# 4. Crear superusuario Django (para el admin)
docker compose exec backend python manage.py createsuperuser
```

**URLs en dev:**
- Frontend (Vite): http://localhost:5173
- Backend (Django): http://localhost:8000
- Admin Django:    http://localhost:8000/admin
- Las llamadas `/api/*` desde el frontend van via proxy a Django — sin CORS

---

## Levantar en PRODUCCIÓN

```bash
# 1. Variables de entorno
cp .env.example .env
# Editá: DEBUG=False, SECRET_KEY real, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS

# 2. Build del frontend
cd frontend && npm install && npm run build && cd ..

# 3. Levantar Django + Nginx
docker compose -f docker-compose.prod.yml up --build -d

# 4. Verificar
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs backend
```

**URLs en prod:**
- Todo por Nginx en el puerto 80 (o 443 con SSL)
- `/api/*` y `/admin/` → proxy a gunicorn
- Todo lo demás → React build estático

---

## Postgres externo en red Docker

Si ya tenés un Postgres corriendo en otra red Docker:

```bash
# En .env:
POSTGRES_HOST=nombre_del_contenedor_postgres
DOCKER_NETWORK=nombre_de_la_red_existente

# En docker-compose.prod.yml el servicio backend
# ya está conectado a db_net (red externa)
```

---

## Endpoints API

| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| POST | `/api/auth/register/` | No | Crear cuenta |
| POST | `/api/auth/login/` | No | Login → tokens |
| POST | `/api/auth/token/refresh/` | No | Renovar access token |
| POST | `/api/auth/logout/` | JWT | Cerrar sesión |
| GET  | `/api/auth/me/` | JWT | Usuario actual |
| GET  | `/api/goals/` | JWT | Listar metas |
| POST | `/api/goals/create/` | JWT | Crear meta (genera plan con IA) |
| GET  | `/api/goals/<id>/` | JWT | Detalle de una meta |
| POST | `/api/progress/steps/<id>/complete/` | JWT | Completar paso |
| POST | `/api/progress/videos/<id>/view/` | JWT | Registrar video visto |
| GET  | `/api/progress/goals/<id>/` | JWT | Progreso de una meta |
| GET  | `/api/progress/streak/` | JWT | Streak del usuario |
| GET  | `/api/progress/logros/` | JWT | Logros del usuario |
