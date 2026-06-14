# Agent System Prompt - Mentor Virtual Backend

Este archivo sirve como memoria persistente y guía de contexto de desarrollo para cualquier Agente de IA que trabaje en este proyecto.

---

## 🎯 Información del Proyecto
**Mentor Virtual** es una plataforma de mentoría accesible e inclusiva.
- **Rama activa principal**: `develop`
- **Enfoque técnico**: Backend REST API accesible, integrado con Docker y PostgreSQL.

---

## 🛠️ Stack Tecnológico
- **Lenguaje**: Python 3.12
- **Framework**: Django 5.0+ / 6.0+ & Django REST Framework (DRF)
- **Base de Datos**: PostgreSQL 15 (Docker) / SQLite3 (Fallback local)
- **Documentación**: OpenAPI 3.0 / Swagger UI (vía `drf-spectacular`)
- **Contenedores**: Docker & Docker Compose

---

## 💾 Contexto Crítico & Reglas de Desarrollo

### 1. Base de Datos Dinámica
En [settings.py](MentorVirtual/settings.py), la conexión a la base de datos se resuelve dinámicamente:
- Si `DATABASE_URL` está definida en el entorno, se parsea usando `urllib.parse` para conectarse a **PostgreSQL**.
- Si no está definida, hace fallback a **SQLite3** (`db.sqlite3`).
- *Cualquier cambio de dependencias debe reflejarse en `requirements.txt`.*

### 2. Señales Automáticas (Django Signals)
El modelo `User` está enlazado a `UserProfile` y `UserConfig` mediante señales en `users/models.py`.
- **Acción**: Al crear un `User`, se disparan las señales `post_save` creando el perfil y la configuración correspondientes.
- **Regla**: **No** instanciar `UserProfile` ni `UserConfig` manualmente durante el registro en las vistas; Django lo hace automáticamente.

### 3. Rutas y Documentación
Toda la documentación interactiva está configurada bajo el path `/api/schema/`:
- **Swagger UI**: `/api/schema/swagger-ui/`
- **ReDoc**: `/api/schema/redoc/`
- **Esquema YAML**: `/api/schema/`

---

## 🗃️ Diccionario de Datos Rápido

- **`auth_user`**: Almacena credenciales de usuario (id, username, password, email, is_active).
- **`users_userprofile`**: Datos del perfil (id, user_id [FK 1:1], phone, avatar_url).
- **`users_userconfig`**: Preferencias de accesibilidad (id, user_id [FK 1:1], font_size ['SMALL', 'MEDIUM', 'LARGE'], high_contrast [bool], voice_guidance [bool]).
- **`authtoken_token`**: Tokens de sesión de DRF (key, user_id [FK 1:1], created).

---

## 🚀 Comandos Útiles

- **Iniciar entorno**: `docker compose up -d --build`
- **Ver logs**: `docker compose logs -f web`
- **Migraciones**: `docker compose exec web python manage.py migrate`
- **Crear Superusuario**: `docker compose exec -e DJANGO_SUPERUSER_PASSWORD=<pass> web python manage.py createsuperuser --username <user> --email <email> --no-input`

---

## 🌿 Normativas de Git y GitHub

### 1. Normativas Estándar para Nombrar Ramas (Git Branching)
La convención más utilizada en entornos profesionales es combinar el tipo de tarea, un identificador de seguimiento (opcional, como el ID de Jira/Trello) y una descripción breve en minúsculas separada por guiones.

**Prefijos Estándar:**
- `feature/` : Nuevas funcionalidades (ej: `feature/login-email`).
- `bugfix/` : Corrección de errores en ramas de desarrollo (ej: `bugfix/qa-password-validation`).
- `hotfix/` : Correcciones críticas urgentes directamente en producción (`main`/`master`).
- `docs/` : Solo cambios en documentación (ej: `docs/swagger-endpoints`).

#### 👤 Integrar el Nombre del Encargado en la Rama
Para identificar rápidamente quién es el dueño de la rama sin perder la estructura estándar, se acostumbra a incluir las iniciales o el nombre de usuario del desarrollador justo después del prefijo.

*Estructura:* `tipo-de-rama/usuario-descripcion-corta`

**Ejemplos prácticos para el equipo:**
- `feature/gmedina-login-email` (Funcionalidad de login por email asignada a Gerardo).
- `bugfix/svera-qa-password-validation` (Corrección de validación asignada a Sofía).
- `docs/gmedina-update-swagger` (Actualización de Swagger).

---

### 2. Normativas Estándar para Commits (Conventional Commits)
Para los mensajes de commit (que en el flujo deben ir estrictamente en inglés), el estándar mundial es **Conventional Commits**. Esto permite saber qué hace un cambio de un solo vistazo.

*Estructura:* `tipo(alcance_opcional): descripción corta en minúsculas y en imperativo`

**Tipos de Commit más comunes:**
- `feat`: Una nueva característica para el usuario (ej: `feat(auth): add password confirmation field`).
- `fix`: La resolución de un bug (ej: `fix(validation): correct regex for uppercase character`).
- `docs`: Cambios exclusivos en la documentación (ej: `docs(swagger): update login response schema`).
- `refactor`: Cambios en el código que no corrigen bugs ni añaden funciones (ej: `refactor(serializers): optimize unique email query`).

---

### 3. Coautoría: ¿Cómo integrar los cambios de alguien que colaboró?
Cuando una persona inicia una rama pero otra colabora o ayuda a terminarla, Git ofrece una herramienta nativa para dar crédito a ambos desarrolladores en el historial. Esto se conoce como **Co-Authored-By**.
GitHub reconoce este estándar automáticamente y mostrará los avatares de ambos desarrolladores en el commit.

#### Cómo realizar un commit colaborativo por terminal:
Al momento de escribir el commit, debes dejar **dos líneas en blanco** después del mensaje principal y agregar la etiqueta `Co-authored-by: Nombre <email>` al final del cuerpo del mensaje.

```bash
git commit -m "fix(validation): fix password matching bug from QA report

Co-authored-by: Sofia Vera <svera@innovalab.com>"
```

> [!WARNING]
> **Regla de oro:** Debe haber exactamente **dos líneas vacías** entre el título del commit y la línea de `Co-authored-by`, de lo contrario Git lo procesará como texto común y GitHub no reconocerá al colaborador.

#### Flujo de trabajo en la misma rama (Git Collaboration):
Si un colaborador va a trabajar en la misma rama, el flujo en la terminal es:

1. **El creador sube la rama:**
   ```bash
   git push origin feature/gmedina-implementar-validaciones
   ```

2. **El colaborador descarga la rama y trabaja en ella:**
   ```bash
   git fetch origin
   git checkout feature/gmedina-implementar-validaciones
   # Hace sus cambios, ayuda a resolver el bug y hace commit:
   git commit -m "feat(validation): add custom errors for empty fields"
   git push origin feature/gmedina-implementar-validaciones
   ```

3. **El creador recupera la ayuda de su compañero:**
   ```bash
   # Antes de seguir programando, el dueño de la rama hace pull:
   git pull origin feature/gmedina-implementar-validaciones
   ```

---

### 📋 Resumen de Buenas Prácticas para el Agente

| Acción | Estándar Sugerido | Ejemplo Real |
| :--- | :--- | :--- |
| **Crear Rama** | `tipo/usuario-tarea` | `feature/gmedina-auth-validations` |
| **Commit Individual** | `tipo(alcance): descripción` (Inglés) | `feat(users): implement strict password rules` |
| **Commit Colaborativo** | Mensaje principal + doble espacio + Co-author | `fix(qa): resolve login bug` <br><br> `Co-authored-by: Name <mail>` |

---

## 📂 Estructura del Proyecto
- `/MentorVirtual`: Configuración del proyecto Django.
- `/users`: Gestión de autenticación, perfiles y accesibilidad.
- `/mentor`: Lógica futura de mentorías.
- `/documentacion`: Guías de la API y modelos de datos.
