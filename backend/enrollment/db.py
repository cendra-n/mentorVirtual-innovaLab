from django.db import connection, transaction
from rest_framework.exceptions import ValidationError
from .models import Enrollment
import logging

logger = logging.getLogger(__name__)

# Función de utilidad (debe ir aquí para que todas las demás la vean)
def _rows_as_dicts(cursor):
    """Convierte las filas de un cursor de SQL en una lista de diccionarios."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

#Lista todos los cursos disponibles is_active=true/ disponible para los 3 roles
def get_available_courses() -> list[dict]:
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM sp_get_available_courses()")
        data = _rows_as_dicts(cur)
        print("DEBUG: Datos recibidos desde DB:", data) # <-- Esto aparecerá en los logs del contenedor
        return data

#Endpoint para que el alumno se anota a un curso activo con validación de 3 incluida desde el sp.   
def enroll_student_in_course(student_id: int, course_id: int) -> int:
    """Inscribe a un alumno aplicando las reglas de negocio."""
    with transaction.atomic():
        with connection.cursor() as cursor:

            # 1. Llamada al SP de inscripción (ahora es el único validador)
            try:
                cursor.execute("SELECT sp_enroll_student(%s, %s);", [student_id, course_id])
                result = cursor.fetchone()
                return result[0] if result else None
            except Exception as e:
                # Aquí logueas el error real para que lo veas en tus archivos de log
                logger.error(f"Error crítico en la inscripción: {str(e)}")

                error_msg = str(e)
                if "LIMIT_REACHED" in error_msg:
                    raise ValidationError({"detail": "Solo puedes estar anotado en 3 cursos."})
                elif "COURSE_NOT_FOUND" in error_msg:
                    raise ValidationError({"course_id": "Error, no hay cursos con este id."})
                elif "COURSE_NOT_ACTIVE" in error_msg:
                    raise ValidationError({"course_id": "Error, no puedes anotarte en un curso inactivo."})
                elif "UNIQUE_STUDENT_COURSE" in error_msg:
                    raise ValidationError({"course_id": "Ya estas anotado en este curso."}) 
                else:
                    # El usuario solo ve esto, pero el error real queda guardado en el log
                    raise ValidationError({"Detalles": "Error inesperado.Por favor intente nuevamente"})

#lista de inscripciones en la view se separara por rol lo que puede ver admin y proffesor
def get_all_enrollments_db() -> list:
    """
    Ejecuta el SP para obtener todas las inscripciones con sus detalles.
    Retorna una lista de diccionarios con:
    enrollment_id, student_email, course_name, professor_name.
    """
    try:
        with connection.cursor() as cursor:
            # Llamamos al procedimiento almacenado que creamos en init_enrollment.sql
            cursor.execute("SELECT * FROM sp_get_all_enrollments();")
            
            # Obtenemos los nombres de las columnas que retorna el SP
            columns = [col[0] for col in cursor.description]
            
            # Convertimos cada fila en un diccionario usando los nombres de columnas
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
            
    except Exception as e:
        # Registramos el error internamente de forma segura
        logger.error(f"Error al obtener lista consolidada de inscripciones: {e}")
        # Retornamos una lista vacía para evitar romper el flujo del front-end
        return []
    

#Endpoint donde el alumno podra ver los cursos a los que esta inscripto

def get_my_enrollments_db(student_email):
    """
    Llama al procedimiento almacenado sp_get_my_enrollments para obtener 
    los cursos del estudiante autenticado.
    """
    results = []
    # Usamos la conexión de Django para ejecutar el procedimiento
    with connection.cursor() as cursor:
        # Llamamos a la función de Postgres como si fuera un SELECT
        cursor.execute("SELECT * FROM sp_get_my_enrollments(%s)", [student_email])
        
        # Obtenemos los nombres de las columnas
        columns = [col[0] for col in cursor.description]
        
        # Convertimos cada fila en un diccionario usando el nombre de la columna
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
            
    return results  
                
