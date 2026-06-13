"""
Capa de datos para progreso, streaks y videos vistos.
Solo stored procedures, sin ORM.
"""
from django.db import connection


# ── User Progress ─────────────────────────────────────────────────────────────

def sp_complete_step(step_id: int, user_id: int) -> dict:
    """
    Marca un paso como completado.
    Devuelve: { step_id, completed, already_completed }
    """
    with connection.cursor() as cur:
        cur.callproc('sp_complete_step', [step_id, user_id])
        row = cur.fetchone()
    cols = ['step_id', 'completed', 'already_completed']
    return dict(zip(cols, row))


def sp_get_user_progress(user_id: int, goal_id: int) -> dict:
    """
    Devuelve progreso global de un goal para el usuario.
    """
    with connection.cursor() as cur:
        cur.callproc('sp_get_user_progress', [user_id, goal_id])
        row = cur.fetchone()
    if not row:
        return {}
    cols = ['goal_id', 'total_steps', 'completed_steps', 'percent_complete', 'goal_completed']
    return dict(zip(cols, row))


# ── Videos vistos ─────────────────────────────────────────────────────────────

def sp_register_video_view(user_id: int, video_id: int, step_id: int) -> dict:
    """
    Registra que el usuario vio un video.
    Devuelve: { view_id, already_viewed }
    """
    with connection.cursor() as cur:
        cur.callproc('sp_register_video_view', [user_id, video_id, step_id])
        row = cur.fetchone()
    cols = ['view_id', 'already_viewed']
    return dict(zip(cols, row))


def sp_get_viewed_videos(user_id: int, goal_id: int) -> list[dict]:
    with connection.cursor() as cur:
        cur.callproc('sp_get_viewed_videos', [user_id, goal_id])
        rows = cur.fetchall()
    cols = ['video_id', 'title', 'step_id', 'viewed_at']
    return [dict(zip(cols, r)) for r in rows]


# ── Streaks ───────────────────────────────────────────────────────────────────

def sp_update_streak(user_id: int) -> dict:
    """
    Actualiza el streak del usuario tras una actividad.
    Devuelve: { current_streak, longest_streak, last_activity }
    """
    with connection.cursor() as cur:
        cur.callproc('sp_update_streak', [user_id])
        row = cur.fetchone()
    cols = ['current_streak', 'longest_streak', 'last_activity']
    return dict(zip(cols, row))


def sp_get_streak(user_id: int) -> dict:
    with connection.cursor() as cur:
        cur.callproc('sp_get_streak', [user_id])
        row = cur.fetchone()
    if not row:
        return {'current_streak': 0, 'longest_streak': 0, 'last_activity': None}
    cols = ['current_streak', 'longest_streak', 'last_activity']
    return dict(zip(cols, row))
