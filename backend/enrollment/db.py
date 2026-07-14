from django.db import connection, transaction
from rest_framework.exceptions import ValidationError

def get_available_courses():
    """
    Obtiene todos los cursos activos que estan listos para que los alumnos se inscriban.
    """
    with connection.cursor() as cursor:
        query = """
            SELECT c.id, c.title, c.description, c.level, c.discipline, 
                   c.objectives, c.cover_image, u.username AS professor_name
            FROM courses_course c
            INNER JOIN auth_user u ON c.professor_id = u.id
            WHERE c.is_active = 1
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def enroll_student_in_course(student_id: int, course_id: int) -> int:
    """
    Inscribe a un alumno en un curso activo, aplicando de forma estricta los limites de negocio.
    Retorna el ID de la inscripcion generada.
    """
    with transaction.atomic():
        with connection.cursor() as cursor:
            # 1. Validar si el curso existe y esta activo
            cursor.execute(
                "SELECT is_active FROM courses_course WHERE id = %s", 
                [course_id]
            )
            course_row = cursor.fetchone()
            
            if not course_row:
                raise ValidationError({"course_id": "The requested course does not exist."})
            
            if not course_row[0]:  # is_active == False
                raise ValidationError({"course_id": "Cannot enroll in an inactive course."})

            # 2. Evitar duplicados (que el alumno se anote dos veces al mismo curso)
            cursor.execute(
                """
                SELECT id FROM enrollment_enrollment 
                WHERE student_id = %s AND course_id = %s AND status = 'active'
                """,
                [student_id, course_id]
            )
            if cursor.fetchone():
                raise ValidationError({"course_id": "You are already actively enrolled in this course."})

            # 3. Validar el tope maximo del alumno (Maximo 3 inscripciones activas)
            cursor.execute(
                "SELECT COUNT(*) FROM enrollment_enrollment WHERE student_id = %s AND status = 'active'",
                [student_id]
            )
            active_enrollments_count = cursor.fetchone()[0]
            if active_enrollments_count >= 3:
                raise ValidationError({"detail": "You have reached the maximum limit of 3 active enrollments."})

            # 4. Insertar la inscripcion en la base de datos
            insert_query = """
                INSERT INTO enrollment_enrollment (student_id, course_id, status, enrolled_at)
                VALUES (%s, %s, 'active', NOW())
            """
            cursor.execute(insert_query, [student_id, course_id])
            
            # Obtener el ID autoincremental generado por la insercion
            cursor.execute("SELECT LAST_INSERT_ID()") 
            enrollment_id = cursor.fetchone()[0]
            
            return enrollment_id


def get_student_dashboard_data(student_id: int):
    """
    Obtiene el perfil del alumno y la lista de los cursos a los que se ha inscrito,
    incluyendo el ID del curso, titulo y el nombre del profesor de forma indirecta.
    """
    with connection.cursor() as cursor:
        # 1. Traer los datos basicos del alumno
        cursor.execute("SELECT id, username, email FROM auth_user WHERE id = %s", [student_id])
        student_row = cursor.fetchone()
        if not student_row:
            return None
        
        # 2. Traer los cursos inscritos cruzando tablas (JOIN) para obtener el profesor
        query_courses = """
            SELECT c.id AS course_id, c.title AS course_title, u.username AS professor_name, e.enrolled_at
            FROM enrollment_enrollment e
            INNER JOIN courses_course c ON e.course_id = c.id
            INNER JOIN auth_user u ON c.professor_id = u.id
            WHERE e.student_id = %s AND e.status = 'active'
        """
        cursor.execute(query_courses, [student_id])
        columns_courses = [col[0] for col in cursor.description]
        enrolled_courses = [dict(zip(columns_courses, row)) for row in cursor.fetchall()]
        
        # 3. Armar la estructura final de respuesta
        return {
            "student_id": student_row[0],
            "student_username": student_row[1],
            "student_email": student_row[2],
            "enrolled_courses_count": len(enrolled_courses),
            "enrolled_courses": enrolled_courses
        }