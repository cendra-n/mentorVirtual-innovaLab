import json
import logging
import urllib.request
import urllib.parse
from django.conf import settings
from core.ai_providers import get_ai_provider

logger = logging.getLogger(__name__)

# Prompt base para estructurar el curso con Anthropic Claude
COURSE_PROMPT_TEMPLATE = """
Eres un diseñador curricular experto en educación adaptativa para adultos mayores.
El usuario quiere crear un curso con las siguientes especificaciones:
- **Tema del curso / Objetivo principal:** "{objetivo_curso}"
- **Nivel de dificultad al que va dirigido:** "{nivel_estudiante}" (Principiante, Medio o Avanzado). Ajusta el vocabulario, la complejidad de las explicaciones y la dificultad de los cuestionarios a este nivel de forma pedagógica y accesible para adultos mayores.
- **Disciplina/Categoría:** "{disciplina}"
- **Objetivos de aprendizaje específicos sugeridos:** "{objetivos_aprendizaje}"

El curso debe constar de exactamente {cantidad_modulos} módulos.

Requisitos de contenido por módulo:
1. Diseña un título claro, ameno y adecuado para el nivel.
2. Genera una consulta de búsqueda de YouTube específica en español para encontrar un video explicativo corto, sencillo y apto para adultos mayores sobre el tema del módulo. La consulta debe alinearse con el nivel del estudiante. Ejemplo: "como usar whatsapp paso a paso principiantes".
3. {pdf_instruction}
4. {quiz_instruction}

Responde ÚNICAMENTE con un objeto JSON válido que siga exactamente la siguiente estructura. No incluyas explicaciones adicionales, introducciones ni bloques de código markdown. Todo el JSON debe estar en español:

{{
  "title": "Título sugerido para el curso",
  "description": "Descripción general y motivadora del curso",
  "level": "{nivel_estudiante_db}",
  "discipline": "{disciplina}",
  "objectives": "Objetivos de aprendizaje del curso consolidados (uno por línea)",
  "cover_image": "Sugerir una URL real de Unsplash relacionada con el tema del curso (ej. https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=800)",
  "modules": [
    {{
      "title": "Título del Módulo",
      "youtube_query": "consulta de búsqueda de YouTube",
      "pdf_title": "Título de la lectura (si aplica, si no, cadena vacía)",
      "pdf_content": "Texto de lectura completo de 2 a 3 párrafos en español, redactado con un lenguaje adecuado al nivel '{nivel_estudiante}' (si aplica, si no, cadena vacía)",
      "quiz": [
        {{
          "question": "Pregunta de opción múltiple",
          "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
          "correct_option_index": 0
        }}
      ]
    }}
  ]
}}
"""


class AnthropicService:
    @staticmethod
    def generate_course_structure(objective: str, num_modules: int, generate_pdfs: bool, generate_quizzes: bool, level: str = 'beginner', discipline: str = 'general', learning_objectives: str = '') -> dict:
        """
        Llama a la Claude API para generar la estructura del curso.
        """
        pdf_instruction = (
            "Genera un título ('pdf_title') y un texto completo de lectura de 2 a 3 párrafos ('pdf_content') para este módulo."
            if generate_pdfs else "Deja 'pdf_title' y 'pdf_content' vacíos."
        )
        quiz_instruction = (
            "Genera una lista ('quiz') de exactamente 3 preguntas de opción múltiple con 4 opciones cada una y el índice de la opción correcta (0-3)."
            if generate_quizzes else "Deja la lista 'quiz' vacía."
        )

        # Mapear nivel de DB a español legible para Claude y viceversa
        level_label_mapping = {
            'beginner': 'Principiante',
            'intermediate': 'Medio',
            'advanced': 'Avanzado',
            'Principiante': 'Principiante',
            'Medio': 'Medio',
            'Avanzado': 'Avanzado'
        }
        level_db_mapping = {
            'Principiante': 'beginner',
            'Medio': 'intermediate',
            'Avanzado': 'advanced',
            'beginner': 'beginner',
            'intermediate': 'intermediate',
            'advanced': 'advanced'
        }

        lang_level = level_label_mapping.get(level, 'Principiante')
        db_level = level_db_mapping.get(level, 'beginner')

        prompt = COURSE_PROMPT_TEMPLATE.format(
            objetivo_curso=objective,
            cantidad_modulos=num_modules,
            nivel_estudiante=lang_level,
            nivel_estudiante_db=db_level,
            disciplina=discipline or 'general',
            objetivos_aprendizaje=learning_objectives or 'Ninguno',
            pdf_instruction=pdf_instruction,
            quiz_instruction=quiz_instruction
        )

        try:
            ai = get_ai_provider()
            raw_text = ai.complete(
                system="Eres un tutor empático y estructurado que responde estrictamente en formato JSON válido.",
                prompt=prompt,
                max_tokens=4000,
            )

            # Limpieza de markdown en caso de que el modelo responda con bloques de código
            raw_text = raw_text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            raw_text = raw_text.strip()

            return json.loads(raw_text)
        except Exception as e:
            logger.error("Error al comunicarse con el proveedor de IA: %s", e)
            raise ValueError(f"No se pudo generar la estructura del curso debido a un error en el servicio de IA: {str(e)}")


class YouTubeService:
    @staticmethod
    def search_course_video(query: str) -> dict | None:
        """
        Busca un video educativo relevante y accesible en español en la API de YouTube.
        """
        # Agregamos palabras clave para orientar los resultados a adultos mayores y explicaciones sencillas
        refined_query = f"{query} explicacion sencilla facil en español"

        params = urllib.parse.urlencode({
            "part": "snippet",
            "q": refined_query,
            "type": "video",
            "maxResults": 1,
            "relevanceLanguage": "es",
            "videoDuration": "medium",  # Limita a videos de entre 4 y 20 minutos
            "safeSearch": "strict",
            "key": settings.YOUTUBE_API_KEY,
        })
        url = f"https://www.googleapis.com/youtube/v3/search?{params}"

        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            items = data.get("items", [])
            if not items:
                # Reintento sin el filtro de duración si no encuentra nada
                params_fallback = urllib.parse.urlencode({
                    "part": "snippet",
                    "q": refined_query,
                    "type": "video",
                    "maxResults": 1,
                    "relevanceLanguage": "es",
                    "safeSearch": "strict",
                    "key": settings.YOUTUBE_API_KEY,
                })
                url_fallback = f"https://www.googleapis.com/youtube/v3/search?{params_fallback}"
                req_fallback = urllib.request.Request(url_fallback, headers={"Accept": "application/json"})
                with urllib.request.urlopen(req_fallback, timeout=15) as resp_fb:
                    data = json.loads(resp_fb.read().decode("utf-8"))
                items = data.get("items", [])

            if not items:
                return None

            item = items[0]
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            return {
                "video_id": video_id,
                "title": snippet["title"],
                "thumbnail": snippet["thumbnails"]["high"]["url"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "channel": snippet["channelTitle"],
            }
        except Exception as e:
            logger.warning("Error al buscar video en YouTube para la consulta '%s': %s", query, e)
            return None


def recalculate_student_course_progress(student, course):
    """
    Recalcula el progreso general del estudiante en un curso considerando pesos ponderados
    para PDFs (30%), Videos YTB (30%) y Cuestionarios (40%), con redistribución automática.
    """
    from django.utils import timezone
    from .models import Lesson, LessonProgress, QuizAttempt, StudentCourseState
    import os
    import json
    from django.conf import settings

    modules = course.modules.all()
    if not modules.exists():
        return 0.0

    total_modules_progress = 0.0

    for module in modules:
        # Pesos estándar por defecto
        w_pdf = 0.3
        w_ytb = 0.3
        w_quiz = 0.4

        # Obtener lecciones del módulo
        lessons = module.lessons.all()
        pdfs = lessons.filter(resource_type='PDF')
        ytbs = lessons.filter(resource_type='YTB')

        # Buscar si el módulo tiene cuestionario en disco
        media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
        quiz_file_path = os.path.join(media_root, 'courses', f"quiz_modulo_{module.id}.json")
        has_quiz = os.path.exists(quiz_file_path)

        # Desactivar pesos si no existen los recursos en este módulo
        if not pdfs.exists():
            w_pdf = 0.0
        if not ytbs.exists():
            w_ytb = 0.0
        if not has_quiz:
            w_quiz = 0.0

        total_weights = w_pdf + w_ytb + w_quiz
        if total_weights == 0.0:
            # Si el módulo está vacío, cuenta como 100% completado
            total_modules_progress += 100.0
            continue

        # Normalizar pesos
        w_pdf_norm = w_pdf / total_weights
        w_ytb_norm = w_ytb / total_weights
        w_quiz_norm = w_quiz / total_weights

        # 1. Progreso de PDFs
        p_pdf = 0.0
        if pdfs.exists():
            completed_pdfs = LessonProgress.objects.filter(
                student=student,
                lesson__in=pdfs,
                is_completed=True
            ).count()
            p_pdf = completed_pdfs / pdfs.count()

        # 2. Progreso de Videos
        p_ytb = 0.0
        if ytbs.exists():
            completed_ytbs = LessonProgress.objects.filter(
                student=student,
                lesson__in=ytbs,
                is_completed=True
            ).count()
            p_ytb = completed_ytbs / ytbs.count()

        # 3. Progreso de Cuestionario (mejor puntuación del intento)
        p_quiz = 0.0
        if has_quiz:
            best_attempt = QuizAttempt.objects.filter(
                student=student,
                module=module
            ).order_by('-score').first()
            if best_attempt:
                p_quiz = best_attempt.score / 100.0

        # Progreso acumulado del módulo
        module_progress = (w_pdf_norm * p_pdf + w_ytb_norm * p_ytb + w_quiz_norm * p_quiz) * 100.0
        total_modules_progress += module_progress

    # Progreso general = Promedio de módulos
    overall_progress = total_modules_progress / modules.count()
    overall_progress = round(overall_progress, 2)

    # Actualizar estado global del estudiante
    state, _ = StudentCourseState.objects.get_or_create(
        student=student,
        course=course
    )
    state.progress_percent = overall_progress

    # Si llega a 100%, marcar completado
    if state.progress_percent >= 100.0 and not state.is_completed:
        state.is_completed = True
        state.completed_at = timezone.now()
        if state.started_at:
            state.total_time_spent = state.completed_at - state.started_at
    elif state.progress_percent < 100.0:
        state.is_completed = False
        state.completed_at = None
        state.total_time_spent = None

    state.save()
    return state.progress_percent

