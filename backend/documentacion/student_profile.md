## Informe Técnico: Ampliación del Perfil del Estudiante (Student Analytics)

## Objetivo

Implementar un modelo de datos escalable para capturar métricas de comportamiento, progreso y engagement de los estudiantes, facilitando la futura explotación de datos para el equipo de Data Analyst.

## Cambios realizados

  #### 1.  Modelado de Datos (models.py)

- Nuevo Modelo StudentProfile: Se creó un modelo exclusivo para métricas de estudiantes, vinculado mediante una relación OneToOneField con el modelo User base.

- Automatización: Se implementaron señales (post_save) que crean el perfil de métricas de forma automática al registrar un nuevo usuario, garantizando integridad referencial.

- Tipos de Datos: Se migraron campos de tiempo a FloatField para permitir una mayor precisión analítica (fracciones de minutos) y se mantuvieron los contadores como PositiveIntegerField para optimizar el rendimiento de la BD.

- Zona Horaria: Se integró el campo zona_horaria con valor por defecto, optimizado para la sincronización de notificaciones.

#### 2. Capa de API y Serialización (serializers.py)

- Seguridad de Datos: Los campos críticos de analítica (rachas, videos vistos, tiempo acumulado) se marcaron como read_only=True para prevenir la manipulación manual de datos por parte del usuario final.

- Validación: Se establecieron min_value y max_value en el serializador para evitar el envío de valores numéricos erróneos o "centinelas" desde el frontend.

#### 3. Configuración y Entorno (Docker/WSL)

- CORS: Se instaló y configuró django-cors-headers para resolver errores de comunicación entre el frontend y el backend en el entorno de desarrollo (Docker/WSL).

- Persistencia: Se ajustó la configuración de Docker para asegurar que las nuevas dependencias se incluyan en el proceso de build.

## Estado actual
El sistema acepta peticiones PATCH de actualización de perfil de manera segura.

Las métricas están protegidas contra escritura externa.

El entorno está listo para la siguiente fase: Registro de eventos analíticos.

## Recomendación:

Para ejecutar correctamente, ejecutar en orden:

- docker compose down

- docker compose build

- docker compose up -d

- docker compose exec backend python manage.py migrate

*Éste último comando, hacerlo desde una terminal aparte.