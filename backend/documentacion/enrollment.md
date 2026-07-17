# Informe Técnico: Sistema de Gestión de Inscripciones (Enrollment Module)

## Objetivo
Centralizar la gestión de altas de inscripciones de alumnos a cursos activos, garantizando la seguridad en el acceso a la información y el cumplimiento de las restricciones de negocio según el rol del usuario autenticado.

## Endpoints Implementados

| Endpoint | Método | Rol Permitido | Descripción |
| :--- | :--- | :--- | :--- |
| `/enrollment/courses/available/` | `GET` | Todos (Autenticados) | Lista los cursos disponibles para inscripción. |
| `/enrollment/enroll/` | `POST` | STUDENT | Ejecuta la inscripción de un alumno autenticado a un curso. |
| `/enrollment/enrollments/list/` | `GET` | ADMIN / PROFESSOR | Devuelve el listado completo de inscripciones del sistema. |
| `/enrollment/enrollments/my-courses/` | `GET` | STUDENT | Permite al estudiante ver exclusivamente sus propios cursos inscritos. |

## Especificaciones Técnicas

### 1. Seguridad y Control de Acceso
- **Restricción basada en roles:** Todos los endpoints están protegidos mediante el sistema de permisos de Django REST Framework, validando que el usuario posea el perfil requerido (`IsAuthenticated` y control de rol).
- **Seguridad en `my-courses`:** El endpoint `/enrollments/my-courses/` implementa una validación estricta de perfil. Si el usuario intenta acceder y no tiene el rol de `STUDENT`, el sistema bloquea la petición con un código `403 Forbidden`.

### 2. Capa de Datos y Rendimiento
- **Stored Procedure (PostgreSQL):** La consulta de inscripciones se optimizó utilizando un procedimiento almacenado (`sp_get_my_enrollments`) en la base de datos PostgreSQL, lo cual garantiza integridad y eficiencia al recuperar datos vinculados entre `enrollment`, `auth_user` y `courses`.
- **Serialización Específica:** Se implementó `EnrollmentListSerializerStudent` para asegurar que la respuesta JSON contenga únicamente los campos necesarios para el alumno, manteniendo la limpieza del objeto de respuesta.

### 3. Suite de Pruebas (Testing)
- Se desarrolló la clase `MyEnrollmentsAPITest` para blindar el módulo de inscripciones.
- La suite cubre:
    - **Happy Path:** Acceso exitoso del estudiante a sus cursos.
    - **Validación de Rol:** Denegación de acceso para administradores en endpoints de alumnos.
    - **Seguridad:** Verificación de error `401 Unauthorized` para usuarios no autenticados.
- Se implementó la creación dinámica del Stored Procedure mediante `setUpClass` para asegurar que el entorno de pruebas replique fielmente la lógica de producción.

## Estado actual
- El módulo cuenta con cobertura total de pruebas funcionales (éxito 100% en `enrollment.tests`).
- La integración con el frontend está garantizada a través de la API documentada en Swagger.