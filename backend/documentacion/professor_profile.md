## Informe Técnico: Ampliación del Perfil del Profesor (Professor Lifecycle & Course Management)

## Objetivo

Implementar un ecosistema robusto para la gestión de perfiles de profesores y la instanciación de cursos, garantizando el aislamiento de flujos tradicionales versus inteligencia artificial y asegurando las restricciones de negocio fijadas para el MVP.

## Cambios realizados

#### 1. Modelado de Datos y Ciclo de Vida (models.py)

- **Relación de Unicidad:** Se configuró el campo `professor` en el modelo `Course` utilizando una relación `OneToOneField` vinculada al modelo `User` base. Esto restringe estructuralmente que un usuario docente maneje más de una entidad de curso en esta fase (MVP)
- **Estado Inicial Seguro:** Por regla estricta de negocio, los cursos recién instanciados nacen con el flag `is_active=False`. El curso permanecerá inactivo y ligado al profesor hasta la futura implementación del endpoint de carga de material didáctico, momento en el cual se activará el sistema de forma diferida.

#### 2. Capa de API, Serialización y Vistas (views.py / serializers.py)

- **Creación por Administración:** Se habilitó el flujo jerárquico donde un usuario con rol `ADMIN` posee los permisos necesarios para dar de alta cuentas de profesores en el sistema.
- **Segmentación de Endpoints (Flujos Espejo):** El proceso de creación se dividió en dos arquitecturas independientes utilizando el mismo esquema de campos requeridos (`title`, `description`, `level`, `discipline`, `objectives`):
  - *Módulo Manual (Gestionado por Nadia):* Valida y procesa los datos tradicionales directo en el ORM.
  - *Módulo de Inteligencia Artificial (Gestionado por Gerardo):* Espacio reservado y aislado para la futura inyección de prompts y lógica generativa sin alterar el flujo manual.
- **Filtrado Dinámico en Listados (`GET`):** Se optimizó la vista general de cursos según el token de sesión:
  - Si el rol es `ADMIN`, el ORM retorna la totalidad de los cursos.
  - Si el rol es `PROFESSOR`, el sistema aplica un filtro quirúrgico retornando únicamente su curso asociado.

- **Formateo Estético de Salida (UX):** Se modificó la serialización manual en la respuesta del listado general para omitir la exposición de emails técnicos o corporativos. Mediante `.replace('.', ' ')`, el backend transforma el `username` dinámicamente para devolver nombres limpios en Swagger (ejemplo: `"maria lopez"`).
Como en el campo "username" profesor debe llevar el nombre del docente, desde swagger se puede escribir "Maria Lopez", en la BD se guarda Maria.Lopez y mediante código se hace el .replace para que el usuario vuelva a ver el nombre sin el ".".
En user.serializer se agrega una función que controla si este replace debe hacerse o no dentro de la lista de usuarios, ya que el rol admin y estudiante pueden tener su username como admin02 y pepito01 en student.

En `user.serializer`:
```python
    # Esto lo que hace es analizar los usuarios y los que tengan rol profesor, estan asi en la db : maria.lopez
    # Con esta función lo que hacemos es que ponga un espacio y saque ese punto a nivel visual desde swagger
    # Pero en la db no hay cambios queda maria.lopez , igualmente el usuario agrega nombre y apellido separado
    # Y en la BD se guarda con el punto 
    def to_representation(self, instance):
        """
        Filtro puramente estético de salida JSON. 
        Reemplaza el punto por espacio SOLAMENTE si el rol es de profesor.
        """
        representation = super().to_representation(instance)
        user_role = representation.get('role')
        
        if user_role == 'PROFESSOR' and 'username' in representation and representation['username']:
            representation['username'] = representation['username'].replace('.', ' ')
            
        return representation

- 'En pruebas y validaciones de professor:' Se agrega la clase tests_professor en user para agregar los test
Se agrega el control sobre la fecha de nacimiento el profesor debe tener entre 18 y 65 años
- 'En pruebas y validaciones de cursos:' Se agregan los test dentro del modulo de courses

#### 3. Configuración y Entorno (Docker / Base de Datos)

- **Persistencia PostgreSQL:** Se validó la correcta conexión de los contenedores Docker hacia la base de datos centralizada del proyecto (`MentorVirtual`), asegurando la correcta integridad referencial al consultar tablas como `users_userprofile`.

## Estado actual

- El sistema valida la restricción de un único curso activo por profesor.
- Los listados generales exponen de manera elegante y consistente los nombres de los docentes en la interfaz de Swagger.
- La suite de pruebas está completamente blindada: se ejecutaron los 28 tests automatizados obteniendo un éxito del 100% (0 fallos).


## Recomendación para el equipo:

Para levantar el entorno local con los nuevos cambios estéticos y estructurales, ejecutar en la terminal:

- docker compose up -d --build
- docker compose exec backend python manage.py migrate

*Nota: El flag `--build` asegura que Docker recompile cualquier cambio en las dependencias o configuración en un solo paso, sin necesidad de apagar manualmente los contenedores primero.*