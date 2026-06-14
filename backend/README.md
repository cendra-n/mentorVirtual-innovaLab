# API de Mentor Virtual (Backend)

Este repositorio contiene la API REST y el sistema de base de datos para la plataforma **Mentor Virtual**, un servicio de mentoría personalizada y accesible.

---

## 🎯 Visión y Objetivos del Proyecto

El **Mentor Virtual** es una aplicación diseñada para apoyar a adultos con dificultades para mantener hábitos de estudio, abordando problemas comunes como la frustración, la baja confianza y la falta de acompañamiento. Su objetivo principal es reducir el abandono educativo mediante una experiencia de aprendizaje positiva, motivadora y estructurada.

### 💡 Propuesta de Valor
La app no se limita a impartir clases, sino que se enfoca en la constancia mediante:
- **Mentoría diaria:** Interacción con un avatar que brinda motivación, feedback y seguimiento.
- **Gamificación y hábitos:** Desafíos breves, registro de rachas y un sistema de logros para reforzar el compromiso.
- **Contenido personalizado:** Feed de videos cortos adaptados a los intereses del usuario.

### 📋 Requisitos del MVP
- **Funcionalidades del MVP:** Registro de usuario, feed de videos funcional, mentor virtual básico (mensajes de texto), desafíos estáticos y visualización de progreso/logros.
- **Enfoque Tecnológico:**
  - **Frontend:** React/React Native para plataformas web y móviles.
  - **Backend (Este repositorio):** Desarrollado en Django y Django REST Framework, proporcionando autenticación de usuarios mediante tokens y perfiles de accesibilidad optimizados.
  - **Base de Datos:** PostgreSQL en contenedores Docker y SQLite3 local como base de datos de respaldo.

### 📅 Plan de Trabajo (12 semanas)
El proyecto se organiza en 6 Sprints de desarrollo:
- **Sprints 1-2 (Exploración e Ideación):** Definición de usuarios, flujo de navegación, wireframes y prototipos navegables.
- **Sprints 3-4 (Desarrollo):** Implementación de autenticación, feed de videos, desafíos, logros y lógica del mentor virtual.
- **Sprint 5 (Iteración):** Mejora de la experiencia de usuario (UX), optimización de lógica y validación de estabilidad.
- **Sprint 6 (Cierre):** Despliegue en producción y preparación para el Demo Day.

---

## 🛠️ Tecnologías del Backend
Este backend está construido sobre las siguientes tecnologías:
- **Core**: Python 3.12, Django 5.0+ / 6.0+
- **REST API**: Django REST Framework (DRF)
- **Documentación Interactiva**: `drf-spectacular` (Swagger UI & ReDoc)
- **Base de Datos**: PostgreSQL 15 (en Docker) y SQLite3 (fallback local)
- **Contenedores**: Docker & Docker Compose

---

## 🚀 Guía de Instalación y Ejecución

### 1. Clonar el Proyecto
```bash
git clone https://github.com/equipo-1-innovalab-2026/equipo1-tm-innova-lab-2026-backend.git
cd equipo1-tm-innova-lab-2026-backend
```

### 2. Levantar con Docker
Asegúrate de tener Docker y Docker Compose corriendo. Ejecuta:
```bash
docker compose up -d --build
```
Esto creará la red del proyecto, el volumen de datos de PostgreSQL y levantará los servicios:
- `db` (PostgreSQL en el puerto `5432`)
- `web` (Servidor Django en el puerto `8000`)

### 3. Ejecutar Migraciones de Base de Datos
Crea las tablas necesarias en la base de datos PostgreSQL ejecutando:
```bash
docker compose exec web python manage.py migrate
```

### 4. Crear un Superusuario (Administrador)
Para acceder al panel de administración de Django, crea un administrador:
```bash
docker compose exec web python manage.py createsuperuser
```
*(Sigue las instrucciones en consola para definir usuario, email y contraseña).*

### 5. Verificar que el Sistema esté Corriendo
Abre tu navegador e ingresa a:
- **Developer Portal**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) (Portal centralizado con la documentación interactiva, Swagger, ReDoc y el Diccionario de Datos).
- **Swagger UI**: [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- **ReDoc**: [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/)
- **Panel de Administración**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 📁 Estructura del Proyecto

- `/MentorVirtual`: Configuración global de Django (settings, urls, wsgi).
- `/users`: Aplicación de Django que maneja el registro, autenticación, perfiles y configuraciones de accesibilidad.
- `/mentor`: Aplicación dedicada a la lógica futura de mentorías.
- `/documentacion`: Documentación detallada del proyecto.
  - [Endpoints de la API](documentacion/endpoints_guide.md)
  - [Diccionario de Datos](documentacion/data_dictionary.md)
