"""
Servicios externos:
  - IA (proveedor configurado en .env) → genera plan adaptativo (pasos + logros)
  - YouTube API → busca videos reales para cada paso
"""
import json
import logging
import urllib.request
import urllib.parse

from django.conf import settings

from core.ai_providers import get_ai_provider

logger = logging.getLogger(__name__)


# ── IA (proveedor configurado en AI_PROVIDER) ─────────────────────────────────

PLAN_SYSTEM = "Respondé siempre en español rioplatense. Sé empático, claro y motivador. Usá ejemplos de la vida cotidiana. Máximo 3 párrafos por respuesta."

PLAN_PROMPT = """
Eres un mentor educativo empático que ayuda a adultos que no completaron su educación formal.

El usuario quiere alcanzar esta meta: "{goal_text}"

Generá un plan de aprendizaje personalizado en español con:
- Entre 4 y 7 pasos concretos, ordenados de menor a mayor dificultad
- Para cada paso: un título corto, una descripción motivadora (2-3 oraciones), y palabras clave para buscar un video en YouTube
- 3 logros (badges) que el usuario puede desbloquear al completar hitos del plan

Respondé ÚNICAMENTE con un JSON válido con esta estructura (sin texto extra, sin markdown):
{{
  "steps": [
    {{
      "order": 1,
      "title": "Título del paso",
      "description": "Descripción motivadora",
      "youtube_query": "palabras clave para YouTube"
    }}
  ],
  "logros": [
    {{
      "name": "Nombre del logro",
      "description": "Condición para obtenerlo",
      "icon": "emoji"
    }}
  ]
}}
"""


def generate_plan_with_ai(goal_text: str) -> dict:
    """Llama al proveedor de IA configurado y devuelve el plan como dict."""
    ai = get_ai_provider()
    raw_text = ai.complete(
        system=PLAN_SYSTEM,
        prompt=PLAN_PROMPT.format(goal_text=goal_text),
        max_tokens=settings.GOALS_PLAN_MAX_TOKENS,
    )

    # Limpiar posibles markdown fences
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    return json.loads(raw_text)


# ── YouTube Data API v3 ───────────────────────────────────────────────────────

def search_youtube_video(query: str) -> dict | None:
    """
    Busca el primer video relevante en YouTube para un paso del plan.
    Devuelve dict con video_id, title, thumbnail o None si falla.
    """
    params = urllib.parse.urlencode({
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 1,
        "relevanceLanguage": "es",
        "safeSearch": "strict",
        "key": settings.YOUTUBE_API_KEY,
    })
    url = f"https://www.googleapis.com/youtube/v3/search?{params}"

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        items = data.get("items", [])
        if not items:
            return None

        item = items[0]
        video_id = item["id"]["videoId"]
        snippet  = item["snippet"]

        return {
            "video_id":   video_id,
            "title":      snippet["title"],
            "thumbnail":  snippet["thumbnails"]["high"]["url"],
            "url":        f"https://www.youtube.com/watch?v={video_id}",
            "channel":    snippet["channelTitle"],
        }
    except Exception as exc:
        logger.warning("YouTube API error para query '%s': %s", query, exc)
        return None
