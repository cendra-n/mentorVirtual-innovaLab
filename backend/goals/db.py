"""
Capa de acceso a datos para tablas propias.
NUNCA usa el ORM de Django — solo connection.cursor() con stored procedures.
"""
from django.db import connection


# ── Goals ─────────────────────────────────────────────────────────────────────

def sp_get_goal_by_user_and_text(user_id: int, goal_text: str) -> dict | None:
    with connection.cursor() as cur:
        cur.callproc('sp_get_goal_by_user_and_text', [user_id, goal_text])
        row = cur.fetchone()
    if not row:
        return None
    cols = ['id', 'user_id', 'goal_text', 'status', 'created_at']
    return dict(zip(cols, row))


def sp_create_goal(user_id: int, goal_text: str) -> int:
    """Inserta una meta y devuelve su ID."""
    with connection.cursor() as cur:
        cur.callproc('sp_create_goal', [user_id, goal_text])
        row = cur.fetchone()
    return row[0]


def sp_get_goals_by_user(user_id: int) -> list[dict]:
    with connection.cursor() as cur:
        cur.callproc('sp_get_goals_by_user', [user_id])
        rows = cur.fetchall()
    cols = ['id', 'goal_text', 'status', 'created_at', 'total_steps', 'completed_steps']
    return [dict(zip(cols, r)) for r in rows]


def sp_get_goal_detail(goal_id: int, user_id: int) -> dict | None:
    with connection.cursor() as cur:
        cur.callproc('sp_get_goal_detail', [goal_id, user_id])
        row = cur.fetchone()
    if not row:
        return None
    cols = ['id', 'user_id', 'goal_text', 'status', 'created_at']
    return dict(zip(cols, row))


# ── Steps ─────────────────────────────────────────────────────────────────────

def sp_create_step(goal_id: int, order: int, title: str, description: str, youtube_query: str) -> int:
    with connection.cursor() as cur:
        cur.callproc('sp_create_step', [goal_id, order, title, description, youtube_query])
        row = cur.fetchone()
    return row[0]


def sp_get_steps_by_goal(goal_id: int, user_id: int) -> list[dict]:
    with connection.cursor() as cur:
        cur.callproc('sp_get_steps_by_goal', [goal_id, user_id])
        rows = cur.fetchall()
    cols = ['id', 'goal_id', 'order', 'title', 'description', 'completed', 'completed_at']
    return [dict(zip(cols, r)) for r in rows]


# ── Videos ────────────────────────────────────────────────────────────────────

def sp_save_video(step_id: int, video_id: str, title: str, thumbnail: str, url: str, channel: str) -> int:
    with connection.cursor() as cur:
        cur.callproc('sp_save_video', [step_id, video_id, title, thumbnail, url, channel])
        row = cur.fetchone()
    return row[0]


def sp_get_videos_by_step(step_id: int) -> list[dict]:
    with connection.cursor() as cur:
        cur.callproc('sp_get_videos_by_step', [step_id])
        rows = cur.fetchall()
    cols = ['id', 'step_id', 'video_id', 'title', 'thumbnail', 'url', 'channel']
    return [dict(zip(cols, r)) for r in rows]


# ── Logros ────────────────────────────────────────────────────────────────────

def sp_create_logro(goal_id: int, name: str, description: str, icon: str) -> int:
    with connection.cursor() as cur:
        cur.callproc('sp_create_logro', [goal_id, name, description, icon])
        row = cur.fetchone()
    return row[0]


def sp_get_logros_by_goal(goal_id: int) -> list[dict]:
    with connection.cursor() as cur:
        cur.callproc('sp_get_logros_by_goal', [goal_id])
        rows = cur.fetchall()
    cols = ['id', 'goal_id', 'name', 'description', 'icon', 'unlocked', 'unlocked_at']
    return [dict(zip(cols, r)) for r in rows]


def sp_get_user_logros(user_id: int) -> list[dict]:
    with connection.cursor() as cur:
        cur.callproc('sp_get_user_logros', [user_id])
        rows = cur.fetchall()
    cols = ['id', 'goal_id', 'goal_text', 'name', 'description', 'icon', 'unlocked', 'unlocked_at']
    return [dict(zip(cols, r)) for r in rows]


def sp_unlock_logro_if_eligible(goal_id: int, user_id: int) -> list[dict]:
    """Devuelve logros recién desbloqueados (si los hay)."""
    with connection.cursor() as cur:
        cur.callproc('sp_unlock_logro_if_eligible', [goal_id, user_id])
        rows = cur.fetchall()
    cols = ['id', 'name', 'description', 'icon']
    return [dict(zip(cols, r)) for r in rows]
