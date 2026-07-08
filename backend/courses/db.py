"""
courses/db.py (v2 — reconciliado contra el schema real de courses/ger-ia)

Capa de acceso a datos para courses. NUNCA usa el ORM de Django — solo
connection.cursor() con stored procedures, mismo patrón que goals/db.py.

Respecto a la v1 (basada en un schema hipotético), esta versión:
  - Usa los nombres reales de campo (module_order, lesson_order,
    duration, resource_type PDF/YTB, resource_url, transcription).
  - No modela una tabla de "enrollment" explícita — la inscripción es
    implícita vía student_course_state, igual que en el código original
    de Gerardo (se crea con la primera interacción del alumno).
  - Recibe el rol real del sistema ('ADMIN'/'PROFESSOR'/'STUDENT' desde
    UserProfile.role, no request.user.is_staff).
  - FIX de seguridad: el quiz vive en la tabla module_quiz, nunca en un
    archivo de disco. save_module_quiz()/get_module_quiz_for_student()/
    submit_quiz() son las únicas puertas de entrada — la clave de
    respuestas (correct_option_index) nunca sale de Postgres.
  - FIX de timezone: get_inactivity_alerts() compara en
    America/Argentina/Buenos_Aires, no en UTC.
"""
from django.db import connection
from django.db.utils import DatabaseError


# ─────────────────────────────────────────────────────────────────────
# Excepciones de dominio
# ─────────────────────────────────────────────────────────────────────

class CourseError(Exception):
    pass


class MaxCoursesReached(CourseError):
    pass


class CourseNotFound(CourseError):
    pass


class PermissionDenied(CourseError):
    pass


class QuizNotFound(CourseError):
    pass


class QuizEmpty(CourseError):
    pass


class StateNotFound(CourseError):
    pass


class LessonNotFound(CourseError):
    pass


_ERRCODE_MAP = {
    'P0001': MaxCoursesReached,
    'P0002': CourseNotFound,
    'P0003': PermissionDenied,
    'P0006': QuizNotFound,
    'P0007': QuizEmpty,
    'P0008': StateNotFound,
    'P0009': LessonNotFound,
}


def _translate_db_error(exc: DatabaseError) -> CourseError:
    diag = getattr(getattr(exc, '__cause__', None), 'diag', None)
    code = getattr(diag, 'sqlstate', None) if diag else None
    exc_cls = _ERRCODE_MAP.get(code, CourseError)
    return exc_cls(str(exc))


def _rows_as_dicts(cur) -> list[dict]:
    cols = [c.name for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


# ─────────────────────────────────────────────────────────────────────
# Cursos
# ─────────────────────────────────────────────────────────────────────

def get_courses_for_user(user_id: int, role: str) -> list[dict]:
    """role: 'ADMIN' | 'PROFESSOR' | 'STUDENT'. Calculalo igual que
    permissions.get_user_role antes de llamar acá (superuser/is_staff
    -> 'ADMIN'; si no, profile.role; default 'STUDENT')."""
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM sp_get_visible_courses(%s, %s)", [user_id, role])
        return _rows_as_dicts(cur)


def get_course_detail(course_id: int) -> dict | None:
    """Curso con módulos y lecciones anidados (incluye has_quiz por
    módulo). None si no existe."""
    import json
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM sp_get_course_detail(%s)", [course_id])
        rows = _rows_as_dicts(cur)
        if rows:
            course = rows[0]
            if 'modules' in course and isinstance(course['modules'], str):
                course['modules'] = json.loads(course['modules'])
            return course
        return None


def create_course_manual(professor_id: int, title: str, description: str,
                          level: str, discipline: str, objectives: str,
                          cover_image: str = "", max_courses: int = 2) -> int:
    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT sp_create_course(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [professor_id, title, description, level, discipline,
                 objectives, cover_image, 'manual', max_courses]
            )
            return cur.fetchone()[0]
    except DatabaseError as e:
        raise _translate_db_error(e) from e


def create_course_ai(professor_id: int, title: str, description: str,
                      level: str, discipline: str, objectives: str,
                      cover_image: str = "", max_courses: int = 2) -> int:
    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT sp_create_course(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [professor_id, title, description, level, discipline,
                 objectives, cover_image, 'ai', max_courses]
            )
            return cur.fetchone()[0]
    except DatabaseError as e:
        raise _translate_db_error(e) from e


def update_course(course_id: int, actor_id: int, actor_role: str, **fields) -> bool:
    """fields: title, description, level, discipline, objectives, cover_image."""
    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT sp_update_course(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [course_id, actor_id, actor_role,
                 fields.get('title'), fields.get('description'), fields.get('level'),
                 fields.get('discipline'), fields.get('objectives'), fields.get('cover_image')]
            )
            return cur.fetchone()[0]
    except DatabaseError as e:
        raise _translate_db_error(e) from e


def set_course_active(course_id: int, actor_id: int, actor_role: str, is_active: bool) -> bool:
    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT sp_set_course_active(%s, %s, %s, %s)",
                [course_id, actor_id, actor_role, is_active]
            )
            return cur.fetchone()[0]
    except DatabaseError as e:
        raise _translate_db_error(e) from e


def deactivate_course(course_id: int, actor_id: int, actor_role: str) -> bool:
    return set_course_active(course_id, actor_id, actor_role, False)


def activate_course(course_id: int, actor_id: int, actor_role: str) -> bool:
    return set_course_active(course_id, actor_id, actor_role, True)


# ─────────────────────────────────────────────────────────────────────
# Módulos y lecciones
# ─────────────────────────────────────────────────────────────────────

def add_module(course_id: int, title: str, order: int = None) -> int:
    """order=None => se autoasigna count()+1, igual que el código original."""
    with connection.cursor() as cur:
        cur.execute("SELECT sp_add_module(%s, %s, %s)", [course_id, title, order])
        return cur.fetchone()[0]


def update_module(module_id: int, title: str = None, order: int = None) -> bool:
    with connection.cursor() as cur:
        cur.execute("SELECT sp_update_module(%s, %s, %s)", [module_id, title, order])
        return cur.fetchone()[0]


def delete_module(module_id: int) -> list[str]:
    """Devuelve las resource_url de lecciones PDF para borrado físico:

        paths = delete_module(module_id)
        for p in paths:
            full_path = os.path.join(settings.MEDIA_ROOT, p.replace(settings.MEDIA_URL, '', 1))
            if os.path.exists(full_path):
                os.remove(full_path)
    """
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM sp_delete_module(%s)", [module_id])
        return [r[0] for r in cur.fetchall() if r[0]]


def add_lesson(module_id: int, title: str, duration: str, resource_type: str,
               resource_url: str = "", transcription: str = "", order: int = None) -> int:
    """resource_type: 'PDF' o 'YTB'."""
    with connection.cursor() as cur:
        cur.execute(
            "SELECT sp_add_lesson(%s, %s, %s, %s, %s, %s, %s)",
            [module_id, title, duration, resource_type, resource_url, transcription, order]
        )
        return cur.fetchone()[0]


def update_lesson(lesson_id: int, title: str = None, duration: str = None,
                   resource_type: str = None, resource_url: str = None,
                   transcription: str = None, order: int = None) -> bool:
    with connection.cursor() as cur:
        cur.execute(
            "SELECT sp_update_lesson(%s, %s, %s, %s, %s, %s, %s)",
            [lesson_id, title, duration, resource_type, resource_url, transcription, order]
        )
        return cur.fetchone()[0]


def delete_lesson(lesson_id: int) -> str | None:
    """Devuelve resource_url si era PDF (None si era video), para
    borrado físico del archivo si corresponde."""
    with connection.cursor() as cur:
        cur.execute("SELECT sp_delete_lesson(%s)", [lesson_id])
        row = cur.fetchone()
        return row[0] if row else None


# ─────────────────────────────────────────────────────────────────────
# Quiz — FIX de seguridad: nunca se lee/escribe un archivo en disco,
# y correct_option_index nunca sale de Postgres hacia Python/cliente.
# ─────────────────────────────────────────────────────────────────────

def save_module_quiz(module_id: int, questions: list[dict]) -> bool:
    """questions: [{"question": str, "options": [str, str, str, str],
    "correct_option_index": int}, ...]. Se llama una sola vez al
    generar el curso (manual o IA) — reemplaza la escritura del JSON
    en media/courses/."""
    import json
    with connection.cursor() as cur:
        cur.execute("SELECT sp_save_module_quiz(%s, %s)", [module_id, json.dumps(questions)])
        return cur.fetchone()[0]


def get_module_quiz_for_student(module_id: int) -> list[dict] | None:
    """Versión SIN respuestas correctas, para que el frontend renderice
    el formulario del quiz. None si el módulo no tiene quiz."""
    with connection.cursor() as cur:
        cur.execute("SELECT sp_get_module_quiz_public(%s)", [module_id])
        row = cur.fetchone()
        if row and row[0] is not None:
            val = row[0]
            if isinstance(val, str):
                import json
                val = json.loads(val)
            return val
        return None


def submit_quiz(student_id: int, module_id: int, answers: dict) -> dict:
    """answers: {"0": 2, "1": 0, ...} (índice de pregunta -> índice de
    opción elegida). La corrección ocurre 100% dentro del SP — Python
    nunca ve las respuestas correctas ni las recibe de vuelta.
    Devuelve {"score", "passed", "global_frustration", "wrong_count"}.
    Levanta QuizNotFound / QuizEmpty."""
    import json
    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT * FROM sp_submit_quiz(%s, %s, %s)",
                [student_id, module_id, json.dumps(answers)]
            )
            row = _rows_as_dicts(cur)[0]
            return row
    except DatabaseError as e:
        raise _translate_db_error(e) from e
    finally:
        # El progreso ponderado se recalcula siempre después de un intento,
        # haya pasado o no — igual que hacía la vista original.
        course_id = _get_module_course_id(module_id)
        if course_id:
            recalculate_progress(student_id, course_id)


# ─────────────────────────────────────────────────────────────────────
# Progreso de lecciones
# ─────────────────────────────────────────────────────────────────────

def mark_lesson_progress(student_id: int, lesson_id: int, rating: int = None) -> bool:
    """Idempotente: si ya estaba completada, incrementa attempts y
    actualiza rating/completed_at. Dispara recalculate_progress solo
    con que el llamador lo pida explícitamente (ver vista de ejemplo)."""
    with connection.cursor() as cur:
        cur.execute("SELECT sp_mark_lesson_progress(%s, %s, %s)", [student_id, lesson_id, rating])
        return cur.fetchone()[0]


def recalculate_progress(student_id: int, course_id: int) -> dict:
    """Replica el algoritmo ponderado 30% PDF / 30% video / 40% quiz
    con redistribución. Devuelve {"progress_percent", "is_completed"}."""
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM sp_recalculate_progress(%s, %s)", [student_id, course_id])
        return _rows_as_dicts(cur)[0]


def get_student_course_state(student_id: int, course_id: int) -> dict:
    """Levanta StateNotFound si el alumno no tiene registro de
    progreso en el curso (equivalente al 404 original)."""
    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT * FROM sp_get_student_course_state(%s, %s)",
                [student_id, course_id]
            )
            row = _rows_as_dicts(cur)[0]
            if 'recent_wrong_questions' in row and isinstance(row['recent_wrong_questions'], str):
                import json
                row['recent_wrong_questions'] = json.loads(row['recent_wrong_questions'])
            return row
    except DatabaseError as e:
        raise _translate_db_error(e) from e


def get_course_id_for_lesson(lesson_id: int) -> int:
    """Resuelve course_id a partir de lesson_id (JOIN course_lessons ->
    course_modules -> courses), para vistas como complete_rate_lesson
    que necesitan disparar recalculate_progress() sin armar el JOIN a
    mano. Levanta LessonNotFound si la lección no existe."""
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT sp_get_course_id_for_lesson(%s)", [lesson_id])
            return cur.fetchone()[0]
    except DatabaseError as e:
        raise _translate_db_error(e) from e


def complete_and_rate_lesson(student_id: int, lesson_id: int, rating: int = None) -> dict:
    """Combina mark_lesson_progress + recalculate_progress en un solo
    llamado — es lo que necesita complete_rate_lesson en views.py.
    Devuelve {"progress_percent", "is_completed"}."""
    mark_lesson_progress(student_id, lesson_id, rating)
    course_id = get_course_id_for_lesson(lesson_id)
    return recalculate_progress(student_id, course_id)


def get_inactivity_alerts(days_limit: int = 3) -> list[dict]:
    """FIX de timezone: compara en America/Argentina/Buenos_Aires, no
    UTC. Marca inactivity_alert_sent=True en las filas devueltas
    (mismo efecto secundario que la vista original)."""
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM sp_get_inactivity_alerts(%s)", [days_limit])
        return _rows_as_dicts(cur)


def _get_module_course_id(module_id: int) -> int | None:
    with connection.cursor() as cur:
        cur.execute("SELECT course_id FROM course_modules WHERE id = %s", [module_id])
        row = cur.fetchone()
        return row[0] if row else None
