-- =====================================================================
-- init_enrollment.sql - VERSION REVISADA Y COMPLETA
-- =====================================================================

-- 1. Crear tablas solo si no existen, ignorando errores de FK si las tablas padre aún no están listas
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'enrollment_enrollment') THEN
        CREATE TABLE enrollment_enrollment (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT unique_student_course UNIQUE(student_id, course_id)
        );
    END IF;
END $$;

DROP FUNCTION IF EXISTS sp_get_available_courses();
-- SP 1: Obtener todos los cursos activos.
-- Actualizamos la función para incluir el nombre del profesor
CREATE OR REPLACE FUNCTION sp_get_available_courses()
RETURNS TABLE (
    id INTEGER,
    title VARCHAR,
    description TEXT,
    level VARCHAR,
    discipline VARCHAR,
    objectives TEXT,
    cover_image TEXT,
    generation_type VARCHAR,
    is_active BOOLEAN,
    created_at TIMESTAMPTZ,
    professor_name VARCHAR  -- Nuevo campo
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id, c.title, c.description, c.level, c.discipline, 
        c.objectives, c.cover_image, c.generation_type, 
        c.is_active, c.created_at, u.username AS professor_name
    FROM courses c
    INNER JOIN auth_user u ON c.professor_id = u.id
    WHERE c.is_active = TRUE;
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS sp_enroll_student(INTEGER, INTEGER);

-- SP 2: Inscripción con validación de límite (Máximo 3) si a futuro se cambia, solo se modifica este archivo
CREATE OR REPLACE FUNCTION sp_enroll_student(p_student_id INTEGER, p_course_id INTEGER) 
RETURNS INTEGER AS $$
DECLARE
    v_enrollment_id INTEGER;
    v_is_active BOOLEAN;
    v_count INTEGER;
BEGIN
    SELECT is_active INTO v_is_active FROM courses WHERE id = p_course_id;
    
    IF v_is_active IS NULL THEN
        RAISE EXCEPTION 'COURSE_NOT_FOUND' USING ERRCODE = 'P0002';
    ELSIF v_is_active = FALSE THEN
        RAISE EXCEPTION 'COURSE_NOT_ACTIVE' USING ERRCODE = 'P0010';
    END IF;

    SELECT COUNT(*) INTO v_count FROM enrollment_enrollment 
    WHERE student_id = p_student_id AND status = 'active';

    IF v_count >= 3 THEN
        RAISE EXCEPTION 'LIMIT_REACHED' USING ERRCODE = 'P0011';
    END IF;

    INSERT INTO enrollment_enrollment (student_id, course_id, status, enrolled_at)
    VALUES (p_student_id, p_course_id, 'active', now())
    ON CONFLICT (student_id, course_id) 
    DO UPDATE SET status = 'active', enrolled_at = now()
    RETURNING id INTO v_enrollment_id;

    RETURN v_enrollment_id;
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS sp_get_all_enrollments();
-- SP 3: Obtener lista consolidada de inscripciones

CREATE OR REPLACE FUNCTION sp_get_all_enrollments()
RETURNS TABLE(enrollment_id INTEGER, student_email VARCHAR, course_name VARCHAR, professor_name VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id::INTEGER, 
        u_student.email::VARCHAR, 
        c.title::VARCHAR, 
        u_prof.username::VARCHAR
    FROM enrollment_enrollment e
    INNER JOIN auth_user u_student ON e.student_id = u_student.id
    INNER JOIN courses c ON e.course_id = c.id
    INNER JOIN auth_user u_prof ON c.professor_id = u_prof.id;
END;
$$ LANGUAGE plpgsql;