-- =====================================================================
-- init_courses.sql (v2 — reconciliado contra el schema real de
-- courses/ger-ia, migraciones 0001-0006)
--
-- Arquitectura SP-only: NUNCA se accede a estas tablas vía Django ORM.
-- Reemplaza los modelos Course/Module/Lesson/LessonProgress/
-- QuizAttempt/WrongQuestion/StudentCourseState manteniendo el mismo
-- dominio funcional y los mismos nombres de campo que ya usa el
-- frontend (CoursesPage.tsx), para no romper contrato de API.
--
-- Correcciones respecto al código original de Gerardo:
--   1. BUG DE TIMEZONE en alertas de inactividad — corregido: se
--      compara en America/Argentina/Buenos_Aires, no en UTC.
--   2. RESPUESTAS DE QUIZ EXPUESTAS — corregido: el JSON con
--      preguntas/respuestas correctas pasa de un archivo en
--      media/courses/ (ruta predecible, servida por nginx) a la
--      tabla `module_quiz`. El endpoint que la vista usa para
--      renderizar el quiz al alumno (sp_get_module_quiz_public) NUNCA
--      devuelve correct_option_index. La corrección de respuestas
--      (sp_submit_quiz) ocurre 100% adentro de Postgres — la clave de
--      respuestas nunca viaja a Python ni al cliente.
-- =====================================================================

-- ── Tablas ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS courses (
    id              SERIAL PRIMARY KEY,
    professor_id    INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL DEFAULT '',
    level           VARCHAR(20) NOT NULL DEFAULT 'beginner'
                        CHECK (level IN ('beginner', 'intermediate', 'advanced', 'principiante', 'medio', 'avanzado', 'alto')),
    discipline      VARCHAR(100) NOT NULL DEFAULT 'general',
    objectives      TEXT NOT NULL DEFAULT '',
    cover_image     TEXT NOT NULL DEFAULT '',
    generation_type VARCHAR(10) NOT NULL DEFAULT 'manual'
                        CHECK (generation_type IN ('manual', 'ai')),
    is_active       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_courses_professor ON courses(professor_id);
CREATE INDEX IF NOT EXISTS idx_courses_active ON courses(is_active);

CREATE TABLE IF NOT EXISTS course_modules (
    id           SERIAL PRIMARY KEY,
    course_id    INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title        VARCHAR(255) NOT NULL,
    module_order INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_modules_course ON course_modules(course_id);

CREATE TABLE IF NOT EXISTS course_lessons (
    id            SERIAL PRIMARY KEY,
    module_id     INTEGER NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    title         VARCHAR(255) NOT NULL,
    duration      VARCHAR(50) NOT NULL DEFAULT '15 minutos',
    resource_type CHAR(3) NOT NULL DEFAULT 'PDF' CHECK (resource_type IN ('PDF', 'YTB')),
    resource_url  TEXT NOT NULL DEFAULT '',
    transcription TEXT NOT NULL DEFAULT '',
    lesson_order  INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_lessons_module ON course_lessons(module_id);

-- Reemplaza el archivo quiz_modulo_<id>.json en disco. quiz_data guarda
-- la estructura completa (pregunta, opciones, correct_option_index) y
-- NUNCA se lee directo desde la vista: solo se accede vía SPs que
-- filtran o evalúan las respuestas server-side.
CREATE TABLE IF NOT EXISTS module_quiz (
    module_id  INTEGER PRIMARY KEY REFERENCES course_modules(id) ON DELETE CASCADE,
    quiz_data  JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS lesson_progress (
    id                SERIAL PRIMARY KEY,
    student_id        INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    lesson_id         INTEGER NOT NULL REFERENCES course_lessons(id) ON DELETE CASCADE,
    is_completed      BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at      TIMESTAMPTZ,
    rating            SMALLINT CHECK (rating BETWEEN 1 AND 5),
    attempts          INTEGER NOT NULL DEFAULT 0,
    frustration_level INTEGER NOT NULL DEFAULT 0,
    UNIQUE (student_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id           SERIAL PRIMARY KEY,
    student_id   INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    module_id    INTEGER NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    score        NUMERIC(5,2) NOT NULL,
    passed       BOOLEAN NOT NULL,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_quiz_attempts_student_module ON quiz_attempts(student_id, module_id);

CREATE TABLE IF NOT EXISTS wrong_questions (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    module_id       INTEGER NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    question_text   TEXT NOT NULL,
    selected_option VARCHAR(255) NOT NULL,
    correct_option  VARCHAR(255) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS student_course_state (
    id                     SERIAL PRIMARY KEY,
    student_id             INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    course_id              INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    current_module_id      INTEGER REFERENCES course_modules(id) ON DELETE SET NULL,
    current_lesson_id      INTEGER REFERENCES course_lessons(id) ON DELETE SET NULL,
    progress_percent       NUMERIC(5,2) NOT NULL DEFAULT 0,
    global_frustration     INTEGER NOT NULL DEFAULT 0,
    is_completed           BOOLEAN NOT NULL DEFAULT FALSE,
    started_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at           TIMESTAMPTZ,
    total_time_spent       INTERVAL,
    last_activity          TIMESTAMPTZ NOT NULL DEFAULT now(),
    inactivity_alert_sent  BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (student_id, course_id)
);

CREATE INDEX IF NOT EXISTS idx_scs_student ON student_course_state(student_id);
CREATE INDEX IF NOT EXISTS idx_scs_course ON student_course_state(course_id);


-- =====================================================================
-- SPs — Cursos
-- =====================================================================

CREATE OR REPLACE FUNCTION sp_create_course(
    p_professor_id    INTEGER,
    p_title           VARCHAR,
    p_description     TEXT,
    p_level           VARCHAR,
    p_discipline      VARCHAR,
    p_objectives      TEXT,
    p_cover_image     TEXT,
    p_generation_type VARCHAR,
    p_max_courses     INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_count     INTEGER;
    v_course_id INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM courses WHERE professor_id = p_professor_id;

    IF v_count >= p_max_courses THEN
        RAISE EXCEPTION 'MAX_COURSES_REACHED: profesor % ya tiene % cursos (límite %)',
            p_professor_id, v_count, p_max_courses USING ERRCODE = 'P0001';
    END IF;

    INSERT INTO courses (professor_id, title, description, level, discipline,
                          objectives, cover_image, generation_type, is_active)
    VALUES (p_professor_id, p_title, p_description, p_level, p_discipline,
            p_objectives, p_cover_image, p_generation_type, FALSE)
    RETURNING id INTO v_course_id;

    RETURN v_course_id;
END;
$$ LANGUAGE plpgsql;


-- role: 'ADMIN' | 'PROFESSOR' | 'STUDENT' (calculado en Python igual
-- que permissions.get_user_role: superuser/is_staff -> ADMIN,
-- si no profile.role, default STUDENT).
CREATE OR REPLACE FUNCTION sp_get_visible_courses(
    p_user_id INTEGER,
    p_role    VARCHAR
) RETURNS TABLE (
    id INTEGER, professor_id INTEGER, title VARCHAR, description TEXT,
    level VARCHAR, discipline VARCHAR, objectives TEXT, cover_image TEXT,
    generation_type VARCHAR, is_active BOOLEAN, created_at TIMESTAMPTZ
) AS $$
BEGIN
    IF p_role = 'ADMIN' THEN
        RETURN QUERY SELECT c.id, c.professor_id, c.title, c.description, c.level,
            c.discipline, c.objectives, c.cover_image, c.generation_type,
            c.is_active, c.created_at
        FROM courses c ORDER BY c.created_at DESC;
    ELSIF p_role = 'PROFESSOR' THEN
        RETURN QUERY SELECT c.id, c.professor_id, c.title, c.description, c.level,
            c.discipline, c.objectives, c.cover_image, c.generation_type,
            c.is_active, c.created_at
        FROM courses c WHERE c.professor_id = p_user_id ORDER BY c.created_at DESC;
    ELSE
        RETURN QUERY SELECT c.id, c.professor_id, c.title, c.description, c.level,
            c.discipline, c.objectives, c.cover_image, c.generation_type,
            c.is_active, c.created_at
        FROM courses c WHERE c.is_active = TRUE ORDER BY c.created_at DESC;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_get_course_detail(
    p_course_id INTEGER
) RETURNS TABLE (
    id INTEGER, professor_id INTEGER, title VARCHAR, description TEXT,
    level VARCHAR, discipline VARCHAR, objectives TEXT, cover_image TEXT,
    generation_type VARCHAR, is_active BOOLEAN, modules JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.professor_id, c.title, c.description, c.level, c.discipline,
        c.objectives, c.cover_image, c.generation_type, c.is_active,
        COALESCE((
            SELECT jsonb_agg(
                jsonb_build_object(
                    'id', m.id, 'title', m.title, 'order', m.module_order,
                    'has_quiz', EXISTS(SELECT 1 FROM module_quiz mq WHERE mq.module_id = m.id),
                    'lessons', (
                        SELECT COALESCE(jsonb_agg(
                            jsonb_build_object(
                                'id', l.id, 'title', l.title, 'duration', l.duration,
                                'resource_type', l.resource_type, 'resource_url', l.resource_url,
                                'transcription', l.transcription, 'order', l.lesson_order
                            ) ORDER BY l.lesson_order
                        ), '[]'::jsonb)
                        FROM course_lessons l WHERE l.module_id = m.id
                    )
                ) ORDER BY m.module_order
            )
            FROM course_modules m WHERE m.course_id = c.id
        ), '[]'::jsonb) AS modules
    FROM courses c WHERE c.id = p_course_id;
END;
$$ LANGUAGE plpgsql;


-- p_actor_role: si es 'ADMIN' se salta el chequeo de ownership.
CREATE OR REPLACE FUNCTION sp_update_course(
    p_course_id INTEGER, p_actor_id INTEGER, p_actor_role VARCHAR,
    p_title VARCHAR, p_description TEXT, p_level VARCHAR,
    p_discipline VARCHAR, p_objectives TEXT, p_cover_image TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    v_owner INTEGER;
BEGIN
    SELECT professor_id INTO v_owner FROM courses WHERE id = p_course_id;

    IF v_owner IS NULL THEN
        RAISE EXCEPTION 'COURSE_NOT_FOUND' USING ERRCODE = 'P0002';
    END IF;

    IF p_actor_role != 'ADMIN' AND v_owner != p_actor_id THEN
        RAISE EXCEPTION 'PERMISSION_DENIED' USING ERRCODE = 'P0003';
    END IF;

    UPDATE courses SET
        title = COALESCE(p_title, title), description = COALESCE(p_description, description),
        level = COALESCE(p_level, level), discipline = COALESCE(p_discipline, discipline),
        objectives = COALESCE(p_objectives, objectives), cover_image = COALESCE(p_cover_image, cover_image)
    WHERE id = p_course_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_set_course_active(
    p_course_id INTEGER, p_actor_id INTEGER, p_actor_role VARCHAR, p_is_active BOOLEAN
) RETURNS BOOLEAN AS $$
DECLARE
    v_owner INTEGER;
BEGIN
    SELECT professor_id INTO v_owner FROM courses WHERE id = p_course_id;

    IF v_owner IS NULL THEN
        RAISE EXCEPTION 'COURSE_NOT_FOUND' USING ERRCODE = 'P0002';
    END IF;

    IF p_actor_role != 'ADMIN' AND v_owner != p_actor_id THEN
        RAISE EXCEPTION 'PERMISSION_DENIED' USING ERRCODE = 'P0003';
    END IF;

    UPDATE courses SET is_active = p_is_active WHERE id = p_course_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- =====================================================================
-- SPs — Módulos y Lecciones
-- =====================================================================

CREATE OR REPLACE FUNCTION sp_add_module(
    p_course_id INTEGER, p_title VARCHAR, p_module_order INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_order     INTEGER;
    v_module_id INTEGER;
BEGIN
    v_order := COALESCE(p_module_order, (SELECT COUNT(*) + 1 FROM course_modules WHERE course_id = p_course_id));

    INSERT INTO course_modules (course_id, title, module_order)
    VALUES (p_course_id, p_title, v_order)
    RETURNING id INTO v_module_id;

    RETURN v_module_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_update_module(
    p_module_id INTEGER, p_title VARCHAR, p_module_order INTEGER
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE course_modules SET
        title = COALESCE(p_title, title),
        module_order = COALESCE(p_module_order, module_order)
    WHERE id = p_module_id;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


-- Devuelve resource_url de las lecciones PDF para borrado físico.
-- Cascada en DB: lecciones, quiz, y referencias en student_course_state
-- (SET NULL) se resuelven solas por las FKs.
CREATE OR REPLACE FUNCTION sp_delete_module(
    p_module_id INTEGER
) RETURNS TABLE (resource_url TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT l.resource_url FROM course_lessons l
    WHERE l.module_id = p_module_id AND l.resource_type = 'PDF' AND l.resource_url != '';

    DELETE FROM course_modules WHERE id = p_module_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_add_lesson(
    p_module_id INTEGER, p_title VARCHAR, p_duration VARCHAR,
    p_resource_type CHAR(3), p_resource_url TEXT, p_transcription TEXT,
    p_lesson_order INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_order    INTEGER;
    v_lesson_id INTEGER;
BEGIN
    v_order := COALESCE(p_lesson_order, (SELECT COUNT(*) + 1 FROM course_lessons WHERE module_id = p_module_id));

    INSERT INTO course_lessons (module_id, title, duration, resource_type, resource_url, transcription, lesson_order)
    VALUES (p_module_id, p_title, COALESCE(p_duration, '15 minutos'), p_resource_type,
            COALESCE(p_resource_url, ''), COALESCE(p_transcription, ''), v_order)
    RETURNING id INTO v_lesson_id;

    RETURN v_lesson_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_update_lesson(
    p_lesson_id INTEGER, p_title VARCHAR, p_duration VARCHAR,
    p_resource_type CHAR(3), p_resource_url TEXT, p_transcription TEXT,
    p_lesson_order INTEGER
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE course_lessons SET
        title = COALESCE(p_title, title),
        duration = COALESCE(p_duration, duration),
        resource_type = COALESCE(p_resource_type, resource_type),
        resource_url = COALESCE(p_resource_url, resource_url),
        transcription = COALESCE(p_transcription, transcription),
        lesson_order = COALESCE(p_lesson_order, lesson_order)
    WHERE id = p_lesson_id;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_delete_lesson(
    p_lesson_id INTEGER
) RETURNS TEXT AS $$
DECLARE
    v_url TEXT;
BEGIN
    SELECT resource_url INTO v_url FROM course_lessons
    WHERE id = p_lesson_id AND resource_type = 'PDF';

    DELETE FROM course_lessons WHERE id = p_lesson_id;
    RETURN v_url;
END;
$$ LANGUAGE plpgsql;


-- Resuelve course_id a partir de lesson_id (JOIN course_lessons ->
-- course_modules -> courses). Usado por complete_rate_lesson para
-- disparar sp_recalculate_progress sin que la vista tenga que armar
-- el JOIN a mano.
CREATE OR REPLACE FUNCTION sp_get_course_id_for_lesson(
    p_lesson_id INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_course_id INTEGER;
BEGIN
    SELECT m.course_id INTO v_course_id
    FROM course_lessons l
    JOIN course_modules m ON m.id = l.module_id
    WHERE l.id = p_lesson_id;

    IF v_course_id IS NULL THEN
        RAISE EXCEPTION 'LESSON_NOT_FOUND: lesson % no existe', p_lesson_id
            USING ERRCODE = 'P0009';
    END IF;

    RETURN v_course_id;
END;
$$ LANGUAGE plpgsql;


-- =====================================================================
-- SPs — Quiz (FIX: la clave de respuestas nunca sale de Postgres)
-- =====================================================================

-- quiz_data: [{ "question": "...", "options": ["a","b","c","d"],
--               "correct_option_index": 2 }, ...]
-- Se llama una vez al generar el curso (manual o IA). Reemplaza la
-- escritura del archivo quiz_modulo_<id>.json en disco.
CREATE OR REPLACE FUNCTION sp_save_module_quiz(
    p_module_id INTEGER, p_quiz_data JSONB
) RETURNS BOOLEAN AS $$
BEGIN
    INSERT INTO module_quiz (module_id, quiz_data)
    VALUES (p_module_id, p_quiz_data)
    ON CONFLICT (module_id) DO UPDATE
        SET quiz_data = p_quiz_data, updated_at = now();
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- Versión PÚBLICA del quiz para que el frontend renderice el
-- formulario: pregunta + opciones, SIN correct_option_index. Esta es
-- la función que reemplaza la lectura directa del JSON de disco desde
-- la vista — antes ese archivo se podía pedir entero (con respuesta
-- incluida) si alguien adivinaba la URL de media/.
CREATE OR REPLACE FUNCTION sp_get_module_quiz_public(
    p_module_id INTEGER
) RETURNS JSONB AS $$
DECLARE
    v_quiz JSONB;
BEGIN
    SELECT quiz_data INTO v_quiz FROM module_quiz WHERE module_id = p_module_id;

    IF v_quiz IS NULL THEN
        RETURN NULL;
    END IF;

    RETURN (
        SELECT jsonb_agg(jsonb_build_object('question', q->>'question', 'options', q->'options'))
        FROM jsonb_array_elements(v_quiz) AS q
    );
END;
$$ LANGUAGE plpgsql;


-- Evalúa el quiz 100% server-side: recibe las respuestas del alumno y
-- compara contra quiz_data internamente. correct_option_index nunca
-- se lee desde Python ni se manda al cliente en ningún punto de este
-- flujo. p_answers: {"0": 2, "1": 0, ...} (índice de pregunta -> índice
-- de opción elegida), igual formato que ya arma QuizSubmitSerializer.
CREATE OR REPLACE FUNCTION sp_submit_quiz(
    p_student_id INTEGER, p_module_id INTEGER, p_answers JSONB
) RETURNS TABLE (
    score NUMERIC, passed BOOLEAN, global_frustration INTEGER, wrong_count INTEGER
) AS $$
DECLARE
    v_quiz            JSONB;
    v_total            INTEGER;
    v_correct          INTEGER := 0;
    v_idx              INTEGER := 0;
    v_question         JSONB;
    v_correct_idx      INTEGER;
    v_selected_idx     INTEGER;
    v_options          JSONB;
    v_score            NUMERIC;
    v_passed           BOOLEAN;
    v_course_id        INTEGER;
    v_wrong_count      INTEGER := 0;
    v_new_frustration  INTEGER;
BEGIN
    SELECT quiz_data INTO v_quiz FROM module_quiz WHERE module_id = p_module_id;
    IF v_quiz IS NULL THEN
        RAISE EXCEPTION 'QUIZ_NOT_FOUND: no hay cuestionario para el módulo %', p_module_id
            USING ERRCODE = 'P0006';
    END IF;

    SELECT course_id INTO v_course_id FROM course_modules WHERE id = p_module_id;
    v_total := jsonb_array_length(v_quiz);
    IF v_total = 0 THEN
        RAISE EXCEPTION 'QUIZ_EMPTY' USING ERRCODE = 'P0007';
    END IF;

    FOR v_idx IN 0..(v_total - 1) LOOP
        v_question := v_quiz -> v_idx;
        v_correct_idx := (v_question ->> 'correct_option_index')::INTEGER;
        v_selected_idx := NULLIF(p_answers ->> v_idx::TEXT, '')::INTEGER;
        v_options := v_question -> 'options';

        IF v_selected_idx IS NOT NULL AND v_selected_idx = v_correct_idx THEN
            v_correct := v_correct + 1;
        ELSE
            v_wrong_count := v_wrong_count + 1;
            INSERT INTO wrong_questions (student_id, module_id, question_text, selected_option, correct_option)
            VALUES (
                p_student_id, p_module_id, v_question ->> 'question',
                COALESCE(v_options ->> v_selected_idx, 'Sin responder'),
                COALESCE(v_options ->> v_correct_idx, 'N/A')
            );
        END IF;
    END LOOP;

    v_score := ROUND((v_correct::NUMERIC / v_total) * 100.0, 2);
    v_passed := v_score >= 70.0;

    INSERT INTO quiz_attempts (student_id, module_id, score, passed)
    VALUES (p_student_id, p_module_id, v_score, v_passed);

    -- Asegura que exista el estado del alumno en el curso (equivalente
    -- al get_or_create de StudentCourseState en la vista original).
    INSERT INTO student_course_state (student_id, course_id)
    VALUES (p_student_id, v_course_id)
    ON CONFLICT (student_id, course_id) DO NOTHING;

    IF v_passed THEN
        v_new_frustration := 0;
    ELSE
        SELECT LEAST(s.global_frustration + 1, 5) INTO v_new_frustration
        FROM student_course_state s WHERE s.student_id = p_student_id AND s.course_id = v_course_id;
    END IF;

    UPDATE student_course_state
    SET global_frustration = v_new_frustration, last_activity = now()
    WHERE student_id = p_student_id AND course_id = v_course_id;

    RETURN QUERY SELECT v_score, v_passed, v_new_frustration,
        (CASE WHEN v_passed THEN 0 ELSE v_wrong_count END);
END;
$$ LANGUAGE plpgsql;


-- =====================================================================
-- SPs — Progreso de lecciones y recálculo ponderado
-- =====================================================================

CREATE OR REPLACE FUNCTION sp_mark_lesson_progress(
    p_student_id INTEGER, p_lesson_id INTEGER, p_rating INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_course_id INTEGER;
BEGIN
    SELECT m.course_id INTO v_course_id
    FROM course_lessons l JOIN course_modules m ON m.id = l.module_id
    WHERE l.id = p_lesson_id;

    INSERT INTO lesson_progress (student_id, lesson_id, is_completed, completed_at, rating, attempts)
    VALUES (p_student_id, p_lesson_id, TRUE, now(), p_rating, 1)
    ON CONFLICT (student_id, lesson_id) DO UPDATE
        SET is_completed = TRUE, completed_at = now(), rating = COALESCE(p_rating, lesson_progress.rating),
            attempts = lesson_progress.attempts + 1;

    INSERT INTO student_course_state (student_id, course_id)
    VALUES (p_student_id, v_course_id)
    ON CONFLICT (student_id, course_id) DO UPDATE SET last_activity = now();

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- Replica el algoritmo ponderado 30% PDF / 30% video / 40% quiz de
-- services.recalculate_student_course_progress, con redistribución si
-- falta algún tipo de recurso en el módulo.
CREATE OR REPLACE FUNCTION sp_recalculate_progress(
    p_student_id INTEGER, p_course_id INTEGER
) RETURNS TABLE (progress_percent NUMERIC, is_completed BOOLEAN) AS $$
DECLARE
    v_module           RECORD;
    v_total_progress   NUMERIC := 0;
    v_module_count     INTEGER := 0;
    v_pdf_count        INTEGER;
    v_ytb_count        INTEGER;
    v_has_quiz         BOOLEAN;
    v_w_pdf            NUMERIC;
    v_w_ytb            NUMERIC;
    v_w_quiz           NUMERIC;
    v_total_w          NUMERIC;
    v_p_pdf            NUMERIC;
    v_p_ytb            NUMERIC;
    v_p_quiz           NUMERIC;
    v_completed_pdfs   INTEGER;
    v_completed_ytbs   INTEGER;
    v_best_score       NUMERIC;
    v_module_progress  NUMERIC;
    v_overall          NUMERIC;
    v_was_completed    BOOLEAN;
    v_now_completed    BOOLEAN;
    v_started_at       TIMESTAMPTZ;
BEGIN
    FOR v_module IN SELECT id FROM course_modules WHERE course_id = p_course_id LOOP
        v_module_count := v_module_count + 1;

        SELECT COUNT(*) INTO v_pdf_count FROM course_lessons WHERE module_id = v_module.id AND resource_type = 'PDF';
        SELECT COUNT(*) INTO v_ytb_count FROM course_lessons WHERE module_id = v_module.id AND resource_type = 'YTB';
        SELECT EXISTS(SELECT 1 FROM module_quiz WHERE module_id = v_module.id) INTO v_has_quiz;

        v_w_pdf := CASE WHEN v_pdf_count > 0 THEN 0.3 ELSE 0 END;
        v_w_ytb := CASE WHEN v_ytb_count > 0 THEN 0.3 ELSE 0 END;
        v_w_quiz := CASE WHEN v_has_quiz THEN 0.4 ELSE 0 END;
        v_total_w := v_w_pdf + v_w_ytb + v_w_quiz;

        IF v_total_w = 0 THEN
            v_total_progress := v_total_progress + 100.0;
            CONTINUE;
        END IF;

        v_p_pdf := 0; v_p_ytb := 0; v_p_quiz := 0;

        IF v_pdf_count > 0 THEN
            SELECT COUNT(*) INTO v_completed_pdfs
            FROM lesson_progress lp JOIN course_lessons l ON l.id = lp.lesson_id
            WHERE lp.student_id = p_student_id AND l.module_id = v_module.id
              AND l.resource_type = 'PDF' AND lp.is_completed = TRUE;
            v_p_pdf := v_completed_pdfs::NUMERIC / v_pdf_count;
        END IF;

        IF v_ytb_count > 0 THEN
            SELECT COUNT(*) INTO v_completed_ytbs
            FROM lesson_progress lp JOIN course_lessons l ON l.id = lp.lesson_id
            WHERE lp.student_id = p_student_id AND l.module_id = v_module.id
              AND l.resource_type = 'YTB' AND lp.is_completed = TRUE;
            v_p_ytb := v_completed_ytbs::NUMERIC / v_ytb_count;
        END IF;

        IF v_has_quiz THEN
            SELECT MAX(score) INTO v_best_score
            FROM quiz_attempts WHERE student_id = p_student_id AND module_id = v_module.id;
            v_p_quiz := COALESCE(v_best_score, 0) / 100.0;
        END IF;

        v_module_progress := ((v_w_pdf / v_total_w) * v_p_pdf
                             + (v_w_ytb / v_total_w) * v_p_ytb
                             + (v_w_quiz / v_total_w) * v_p_quiz) * 100.0;

        v_total_progress := v_total_progress + v_module_progress;
    END LOOP;

    IF v_module_count = 0 THEN
        v_overall := 0;
    ELSE
        v_overall := ROUND(v_total_progress / v_module_count, 2);
    END IF;

    INSERT INTO student_course_state AS s (student_id, course_id, progress_percent)
    VALUES (p_student_id, p_course_id, v_overall)
    ON CONFLICT (student_id, course_id) DO UPDATE SET progress_percent = v_overall
    RETURNING s.is_completed, s.started_at INTO v_was_completed, v_started_at;

    v_now_completed := v_overall >= 100.0;

    IF v_now_completed AND NOT v_was_completed THEN
        UPDATE student_course_state SET
            is_completed = TRUE, completed_at = now(),
            total_time_spent = now() - v_started_at
        WHERE student_id = p_student_id AND course_id = p_course_id;
    ELSIF NOT v_now_completed THEN
        UPDATE student_course_state SET
            is_completed = FALSE, completed_at = NULL, total_time_spent = NULL
        WHERE student_id = p_student_id AND course_id = p_course_id;
    END IF;

    RETURN QUERY SELECT v_overall, v_now_completed;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_get_student_course_state(
    p_student_id INTEGER, p_course_id INTEGER
) RETURNS TABLE (
    progress_percent NUMERIC, global_frustration INTEGER, is_completed BOOLEAN,
    last_activity TIMESTAMPTZ, recent_wrong_questions JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT s.progress_percent, s.global_frustration, s.is_completed, s.last_activity,
        COALESCE((
            SELECT jsonb_agg(jsonb_build_object(
                'question_text', wq.question_text, 'selected_option', wq.selected_option,
                'correct_option', wq.correct_option, 'created_at', wq.created_at
            ) ORDER BY wq.created_at DESC)
            FROM (
                SELECT * FROM wrong_questions w
                JOIN course_modules m ON m.id = w.module_id
                WHERE w.student_id = p_student_id AND m.course_id = p_course_id
                ORDER BY w.created_at DESC LIMIT 5
            ) wq
        ), '[]'::jsonb)
    FROM student_course_state s
    WHERE s.student_id = p_student_id AND s.course_id = p_course_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'STATE_NOT_FOUND: sin registro de progreso para student % en course %',
            p_student_id, p_course_id USING ERRCODE = 'P0008';
    END IF;
END;
$$ LANGUAGE plpgsql;


-- FIX del bug de timezone: se compara en hora de Buenos Aires, no UTC.
CREATE OR REPLACE FUNCTION sp_get_inactivity_alerts(
    p_days_limit INTEGER
) RETURNS TABLE (
    student_id INTEGER, student_username VARCHAR, course_id INTEGER,
    course_title VARCHAR, last_activity TIMESTAMPTZ, message TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT s.student_id, u.username, s.course_id, c.title, s.last_activity,
        format('Alerta: el alumno %s lleva más de %s días inactivo en el curso ''%s''.',
               u.username, p_days_limit, c.title)
    FROM student_course_state s
    JOIN auth_user u ON u.id = s.student_id
    JOIN courses c ON c.id = s.course_id
    WHERE s.is_completed = FALSE
      AND s.inactivity_alert_sent = FALSE
      AND (
          (now() AT TIME ZONE 'America/Argentina/Buenos_Aires')
          - (s.last_activity AT TIME ZONE 'America/Argentina/Buenos_Aires')
      ) > (p_days_limit || ' days')::INTERVAL;

    UPDATE student_course_state s SET inactivity_alert_sent = TRUE
    WHERE s.is_completed = FALSE
      AND s.inactivity_alert_sent = FALSE
      AND (
          (now() AT TIME ZONE 'America/Argentina/Buenos_Aires')
          - (s.last_activity AT TIME ZONE 'America/Argentina/Buenos_Aires')
      ) > (p_days_limit || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;
