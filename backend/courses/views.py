# courses/views.py
import os
import json
import logging
import html
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import serializers
from django.db import connection, transaction

from .permissions import get_user_role, IsProfessorOrAdmin
from .serializers import (
    AICourseInputSerializer, AICourseDetailResponseSerializer,
    LessonRatingSerializer, QuizSubmitSerializer, StudentCourseStateSerializer,
    WrongQuestionSerializer, CourseCreationSerializer, ModuleCreateSerializer
)
from .services import AnthropicService, YouTubeService
from courses import db
from courses.db import MaxCoursesReached, CourseNotFound, PermissionDenied, QuizNotFound, QuizEmpty, StateNotFound, LessonNotFound

logger = logging.getLogger(__name__)


def draw_robot_logo():
    from reportlab.graphics.shapes import Drawing, Rect, Circle, Line
    # A small drawing of 40x45 pixels
    d = Drawing(40, 45)
    
    # Antenna
    d.add(Line(20, 32, 20, 40, strokeColor='#1A2A4A', strokeWidth=2))
    d.add(Circle(20, 41, 2.5, fillColor='#00D4FF', strokeColor=None))
    
    # Head
    d.add(Rect(6, 4, 28, 28, rx=6, ry=6, fillColor='#F0F4FF', strokeColor='#1A2A4A', strokeWidth=2))
    
    # Visor
    d.add(Rect(9, 9, 22, 18, rx=4, ry=4, fillColor='#0A1628', strokeColor=None))
    
    # Eyes
    d.add(Circle(14, 18, 2, fillColor='#00D4FF', strokeColor=None))
    d.add(Circle(26, 18, 2, fillColor='#00D4FF', strokeColor=None))
    
    # Mouth
    d.add(Line(16, 13, 24, 13, strokeColor='#00D4FF', strokeWidth=1.5))
    
    return d


def generate_pdf_from_text(pdf_path, title, content, professor_name, course_title, generation_date):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.lib import colors

    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'PDFTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        spaceAfter=15,
        textColor=colors.HexColor('#1A2A4A')
    )
    body_style = ParagraphStyle(
        'PDFBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        spaceAfter=12,
        textColor=colors.HexColor('#333333')
    )
    header_text_style = ParagraphStyle(
        'HeaderDetails',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#555555')
    )
    
    story = []
    
    # Membrete
    logo = draw_robot_logo()
    header_html = f"""
    <b>MENTOR VIRTUAL</b> — <i>PDF Generado por IA y el Mentor</i><br/>
    <b>Curso:</b> {html.escape(course_title)}<br/>
    <b>Profesor:</b> {html.escape(professor_name)} | <b>Fecha:</b> {generation_date}
    """
    header_paragraph = Paragraph(header_html, header_text_style)
    
    # Tabla del membrete
    header_table = Table([[logo, header_paragraph]], colWidths=[50, 450])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
    ]))
    
    story.append(header_table)
    
    # Línea divisoria azul oscuro
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1A2A4A'), spaceBefore=5, spaceAfter=20))
    
    # Título de la lectura
    story.append(Paragraph(html.escape(title), title_style))
    story.append(Spacer(1, 5))
    
    # Contenido de lectura
    paragraphs = content.split('\n')
    for p in paragraphs:
        p_clean = p.strip()
        if p_clean:
            escaped_p = html.escape(p_clean)
            story.append(Paragraph(escaped_p, body_style))
            
    doc.build(story)


class CourseInputSchema(serializers.Serializer):
    title = serializers.CharField(max_length=255, help_text="Nombre del curso")
    description = serializers.CharField(help_text="Texto descriptivo")
    level = serializers.CharField(max_length=50, help_text="Principiante, medio, avanzado")
    discipline = serializers.CharField(max_length=100, help_text="Disciplina a la que pertenece")
    objectives = serializers.CharField(help_text="Objetivos del curso")


@extend_schema(
    methods=['GET'],
    summary="Listado de cursos según rol",
    description="ADMIN: Retorna todos los cursos. PROFESSOR: Retorna el curso del cual es propietario."
)
@extend_schema(
    methods=['POST'],
    request=CourseCreationSerializer,
    summary="Crea un nuevo curso manualmente (Flujo Nadia)",
    description="Crea un curso asociándolo al PROFESSOR. MVP: Nace INACTIVO hasta que se cargue material.",
    examples=[
        OpenApiExample(
            'Ejemplo de Creación de Curso Manual',
            summary='Payload válido con un módulo, lección PDF y un cuestionario estructurado',
            value={
                "title": "Introducción a Python",
                "description": "Curso completo de Python básico a intermedio.",
                "level": "beginner",
                "discipline": "programacion",
                "objectives": "Al final del curso podrás construir pequeños scripts y automatizaciones.",
                "cover_image": "http://example.com/portada-python.jpg",
                "modules": [
                    {
                        "title": "Módulo 1: Sintaxis Básica",
                        "order": 1,
                        "lessons": [
                            {
                                "title": "Variables y Operadores",
                                "duration": "15 minutos",
                                "resource_type": "PDF",
                                "resource_url": "http://example.com/material-python-mod1.pdf",
                                "transcription": "En esta lección aprenderemos sobre tipos de datos...",
                                "order": 1
                            }
                        ],
                        "quiz": [
                            {
                                "question": "¿Cuál es la sintaxis correcta para imprimir en Python?",
                                "options": ["print('Hola')", "echo 'Hola'", "console.log('Hola')"],
                                "correct_option_index": 0
                            },
                            {
                                "question": "¿Qué tipo de dato es el valor True?",
                                "options": ["String", "Integer", "Boolean"],
                                "correct_option_index": 2
                            }
                        ]
                    }
                ]
            },
            request_only=True
        )
    ],
    responses={201: AICourseDetailResponseSerializer, 400: dict}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def course_list_create(request):
    user = request.user
    user_role = get_user_role(user)

    if request.method == 'GET':
        try:
            courses = db.get_courses_for_user(user.id, user_role)
            data = []
            for c in courses:
                with connection.cursor() as cur:
                    cur.execute("SELECT username FROM auth_user WHERE id = %s", [c['professor_id']])
                    row = cur.fetchone()
                    username = row[0] if row else "Sin Profesor"
                
                username_clean = username.replace('.', ' ')
                data.append({
                    "id": c["id"],
                    "title": c["title"],
                    "description": c["description"],
                    "level": c["level"],
                    "discipline": c["discipline"],
                    "objectives": c["objectives"],
                    "cover_image": c["cover_image"],
                    "professor": username_clean,
                    "is_active": c["is_active"],
                })
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Fallo interno al listar cursos: {str(e)}", exc_info=True)
            return Response({"error": "Fallo interno al listar cursos."}, status=500)

    elif request.method == 'POST':
        if user_role not in ['ADMIN', 'PROFESSOR']:
            return Response({"error": "No tenés permisos para crear cursos."}, status=403)

        serializer = CourseCreationSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            error_msg = None
            for key, val in serializer.errors.items():
                if isinstance(val, dict):
                    for k2, v2 in val.items():
                        if isinstance(v2, list) and len(v2) > 0:
                            error_msg = v2[0]
                            break
                elif isinstance(val, list) and len(val) > 0:
                    error_msg = val[0]
                    break
            if error_msg:
                if isinstance(error_msg, dict):
                    for k3, v3 in error_msg.items():
                        if isinstance(v3, list) and len(v3) > 0:
                            error_msg = v3[0]
                            break
                return Response({"error": str(error_msg)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            course_data = serializer.save()
        except MaxCoursesReached:
            return Response(
                {"error": "Un profesor solo puede tener un máximo de 2 cursos a la vez."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error al crear curso manualmente: {str(e)}", exc_info=True)
            return Response({"error": "Error interno al crear curso."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "id": course_data['id'],
                "title": course_data['title'],
                "description": course_data['description'],
                "level": course_data['level'],
                "discipline": course_data['discipline'],
                "objectives": course_data['objectives'],
                "cover_image": course_data['cover_image'],
                "id_user": user.id,
                "professor": user.username,
                "is_active": False,
                "message": "Curso creado exitosamente de forma manual."
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    methods=['POST'],
    request=AICourseInputSerializer,
    summary="Genera la estructura de un curso asistido por IA (Flujo Gerardo)",
    description="Llama al AnthropicService para diseñar el temario y YouTubeService para buscar videos de forma automatizada.",
    responses={201: AICourseDetailResponseSerializer, 400: dict}
)
@api_view(['POST'])
@permission_classes([IsProfessorOrAdmin])
def generate_course_with_ai(request):
    user = request.user
    user_role = get_user_role(user)

    serializer = AICourseInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    objetivo_curso = serializer.validated_data['objetivo_curso']
    cantidad_modulos = serializer.validated_data['cantidad_modulos']
    generar_pdfs = serializer.validated_data['generar_pdfs']
    generar_cuestionarios = serializer.validated_data['generar_cuestionarios']
    level = serializer.validated_data['level']
    discipline = serializer.validated_data['discipline']
    learning_objectives = serializer.validated_data['learning_objectives']
    cover_image = serializer.validated_data['cover_image']

    db_level = 'beginner'
    if level in ['beginner', 'intermediate', 'advanced']:
        db_level = level

    try:
        ia_data = AnthropicService.generate_course_structure(
            objective=objetivo_curso,
            level=db_level,
            discipline=discipline,
            learning_objectives=learning_objectives,
            num_modules=cantidad_modulos,
            generate_pdfs=generar_pdfs,
            generate_quizzes=generar_cuestionarios
        )

        resolved_cover_image = cover_image.strip()
        if not resolved_cover_image:
            resolved_cover_image = ia_data.get('cover_image', '').strip()
            if not resolved_cover_image:
                resolved_cover_image = 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80'

        with transaction.atomic():
            course_id = db.create_course_ai(
                professor_id=user.id,
                title=ia_data.get('title', f"Curso de {objetivo_curso}"),
                description=ia_data.get('description', ''),
                level=db_level,
                discipline=ia_data.get('discipline', discipline),
                objectives=ia_data.get('objectives', learning_objectives or ''),
                cover_image=resolved_cover_image,
                max_courses=settings.MAX_COURSES_PER_PROFESSOR
            )

            quizzes = {}
            modules_data = ia_data.get('modules', [])

            for idx, m_data in enumerate(modules_data, 1):
                module_id = db.add_module(course_id, m_data.get('title', f"Módulo {idx}"), idx)

                lesson_order = 1
                yt_query = m_data.get('youtube_query')
                if yt_query:
                    video_info = YouTubeService.search_course_video(yt_query)
                    if video_info:
                        db.add_lesson(
                            module_id=module_id,
                            title=video_info.get('title', f"Video del Módulo {idx}"),
                            duration="15 minutos",
                            resource_type='YTB',
                            resource_url=video_info.get('url', ''),
                            transcription='',
                            order=lesson_order
                        )
                    else:
                        db.add_lesson(
                            module_id=module_id,
                            title=f"Video introductorio - Módulo {idx}",
                            duration="15 minutos",
                            resource_type='YTB',
                            resource_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            transcription='',
                            order=lesson_order
                        )
                    lesson_order += 1

                if generar_pdfs:
                    pdf_title = m_data.get('pdf_title') or f"Lectura del Módulo {idx}"
                    pdf_content = m_data.get('pdf_content', '')

                    media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
                    courses_media_dir = os.path.join(media_root, 'courses')
                    os.makedirs(courses_media_dir, exist_ok=True)

                    file_name = f"lectura_modulo_{module_id}.pdf"
                    file_path = os.path.join(courses_media_dir, file_name)
                    
                    prof_name = (user.get_full_name() or user.username).replace('.', ' ')
                    gen_date = timezone.now().strftime("%d/%m/%Y")
                    generate_pdf_from_text(
                        pdf_path=file_path,
                        title=pdf_title,
                        content=pdf_content,
                        professor_name=prof_name,
                        course_title=ia_data.get('title', f"Curso de {objetivo_curso}"),
                        generation_date=gen_date
                    )
                    media_url = getattr(settings, 'MEDIA_URL', '/media/')
                    resource_url = f"{media_url}courses/{file_name}"

                    db.add_lesson(
                        module_id=module_id,
                        title=pdf_title,
                        duration="10 minutos",
                        resource_type='PDF',
                        resource_url=resource_url,
                        transcription='',
                        order=lesson_order
                    )
                    lesson_order += 1

                if generar_cuestionarios:
                    quiz_data = m_data.get('quiz', [])
                    db.save_module_quiz(module_id, quiz_data)
                    quizzes[module_id] = quiz_data

            course = db.get_course_detail(course_id)
            serializer = AICourseDetailResponseSerializer(course, context={'quizzes': quizzes})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    except MaxCoursesReached:
        return Response(
            {"error": "Un profesor solo puede tener un máximo de 2 cursos a la vez."},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Fallo al generar curso con IA: {str(e)}", exc_info=True)
        return Response(
            {"error": f"Fallo al generar el curso con IA debido a un error interno: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    methods=['GET', 'PATCH', 'PUT', 'DELETE'],
    summary="Detalle, edición y eliminación de un curso",
    description="Permite a profesores y administradores gestionar un curso. La activación (is_active) está reservada para ADMIN.",
    responses={200: AICourseDetailResponseSerializer, 400: dict}
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def course_detail(request, course_id):
    user = request.user
    user_role = get_user_role(user)

    course = db.get_course_detail(course_id)
    if not course:
        return Response({"error": "Curso no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if not course['is_active']:
        if user_role != 'ADMIN' and course['professor_id'] != user.id:
            return Response(
                {"error": "No tienes permisos para ver este curso en borrador."},
                status=status.HTTP_403_FORBIDDEN
            )

    if request.method == 'GET':
        quizzes = {}
        for module in course.get('modules', []):
            m_id = module['id']
            if user_role in ['ADMIN', 'PROFESSOR']:
                with connection.cursor() as cur:
                    cur.execute("SELECT quiz_data FROM module_quiz WHERE module_id = %s", [m_id])
                    row = cur.fetchone()
                    val = row[0] if row else []
                    if isinstance(val, str):
                        val = json.loads(val)
                    quizzes[m_id] = val
            else:
                quiz = db.get_module_quiz_for_student(m_id)
                quizzes[m_id] = quiz if quiz else []

        serializer = AICourseDetailResponseSerializer(course, context={'quizzes': quizzes})
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        if user_role != 'ADMIN' and course['professor_id'] != user.id:
            return Response(
                {"error": "No tienes permisos para editar este curso."},
                status=status.HTTP_403_FORBIDDEN
            )

        is_active_input = request.data.get('is_active')
        if is_active_input is not None and is_active_input != course['is_active']:
            if user_role != 'ADMIN':
                return Response(
                    {"error": "Solo un administrador puede activar o desactivar cursos en la plataforma."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            db.set_course_active(course_id, user.id, user_role, bool(is_active_input))

        db.update_course(
            course_id=course_id,
            actor_id=user.id,
            actor_role=user_role,
            title=request.data.get('title'),
            description=request.data.get('description'),
            level=request.data.get('level'),
            discipline=request.data.get('discipline'),
            objectives=request.data.get('objectives'),
            cover_image=request.data.get('cover_image')
        )

        if 'modules' in request.data:
            modules_data = request.data.get('modules', [])

            for m_idx, m_data in enumerate(modules_data, 1):
                m_title = m_data.get('title', '').strip()
                if not m_title:
                    return Response(
                        {"error": f"El título del Módulo {m_idx} es obligatorio."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                lessons_data = m_data.get('lessons', [])
                if not lessons_data:
                    return Response(
                        {"error": f"El módulo '{m_title}' debe contener al menos una lección."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                for l_idx, l_data in enumerate(lessons_data, 1):
                    l_title = l_data.get('title', '').strip()
                    l_url = l_data.get('resource_url', '').strip()
                    l_dur = l_data.get('duration', '').strip()
                    if not l_title:
                        return Response(
                            {"error": f"La lección {l_idx} del módulo '{m_title}' debe tener un título."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    if not l_dur:
                        return Response(
                            {"error": f"La lección '{l_title}' del módulo '{m_title}' debe tener una duración."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    if not l_url:
                        return Response(
                            {"error": f"La lección '{l_title}' del módulo '{m_title}' debe tener una URL de recurso (material)."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    res_type = l_data.get('resource_type', 'PDF')
                    if res_type not in ['PDF', 'YTB']:
                        return Response(
                            {"error": f"El tipo de recurso de '{l_title}' debe ser PDF o YTB (YouTube)."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                quiz_data = m_data.get('quiz')
                if quiz_data:
                    if len(quiz_data) < 2:
                        return Response(
                            {"error": f"El cuestionario del Módulo '{m_title}' debe contener al menos 2 preguntas."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    for q_idx, qItem in enumerate(quiz_data):
                        if not qItem.get('question', '').strip():
                            return Response(
                                {"error": f"La pregunta {q_idx + 1} del cuestionario del Módulo '{m_title}' no puede estar vacía."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        options = qItem.get('options', [])
                        if len(options) < 2:
                            return Response(
                                {"error": f"La pregunta {q_idx + 1} del cuestionario del Módulo '{m_title}' debe tener al menos 2 opciones."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        for o_idx, opt in enumerate(options):
                            if not str(opt).strip():
                                return Response(
                                    {"error": f"La opción {o_idx + 1} de la pregunta {q_idx + 1} del cuestionario del Módulo '{m_title}' no puede estar vacía."},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                        correct_idx = qItem.get('correct_option_index')
                        if correct_idx is None or correct_idx < 0 or correct_idx >= len(options):
                            return Response(
                                {"error": f"Selecciona la respuesta correcta para la pregunta {q_idx + 1} del cuestionario del Módulo '{m_title}'."},
                                status=status.HTTP_400_BAD_REQUEST
                            )

            processed_module_ids = []
            for m_idx, m_data in enumerate(modules_data, 1):
                m_id = m_data.get('id')
                m_title = m_data.get('title').strip()
                m_order = m_data.get('order', m_idx)

                if m_id:
                    db.update_module(m_id, m_title, m_order)
                    module_id = m_id
                else:
                    module_id = db.add_module(course_id, m_title, m_order)

                processed_module_ids.append(module_id)

                lessons_data = m_data.get('lessons', [])
                processed_lesson_ids = []
                for l_idx, l_data in enumerate(lessons_data, 1):
                    l_id = l_data.get('id')
                    l_title = l_data.get('title').strip()
                    l_dur = l_data.get('duration').strip()
                    l_res_type = l_data.get('resource_type', 'PDF')
                    l_res_url = l_data.get('resource_url').strip()
                    l_trans = l_data.get('transcription', '')
                    l_order = l_data.get('order', l_idx)

                    if l_id:
                        db.update_lesson(l_id, l_title, l_dur, l_res_type, l_res_url, l_trans, l_order)
                        lesson_id = l_id
                    else:
                        lesson_id = db.add_lesson(module_id, l_title, l_dur, l_res_type, l_res_url, l_trans, l_order)

                    processed_lesson_ids.append(lesson_id)

                with connection.cursor() as cur:
                    cur.execute("SELECT id FROM course_lessons WHERE module_id = %s", [module_id])
                    existing_lesson_ids = [r[0] for r in cur.fetchall()]
                for el_id in existing_lesson_ids:
                    if el_id not in processed_lesson_ids:
                        db.delete_lesson(el_id)

                quiz_data = m_data.get('quiz')
                if quiz_data:
                    db.save_module_quiz(module_id, quiz_data)
                else:
                    with connection.cursor() as cur:
                        cur.execute("DELETE FROM module_quiz WHERE module_id = %s", [module_id])

            with connection.cursor() as cur:
                cur.execute("SELECT id FROM course_modules WHERE course_id = %s", [course_id])
                existing_module_ids = [r[0] for r in cur.fetchall()]
            for em_id in existing_module_ids:
                if em_id not in processed_module_ids:
                    db.delete_module(em_id)

        course = db.get_course_detail(course_id)
        quizzes = {}
        for module in course.get('modules', []):
            m_id = module['id']
            with connection.cursor() as cur:
                cur.execute("SELECT quiz_data FROM module_quiz WHERE module_id = %s", [m_id])
                row = cur.fetchone()
                val = row[0] if row else []
                if isinstance(val, str):
                    val = json.loads(val)
                quizzes[m_id] = val
        serializer = AICourseDetailResponseSerializer(course, context={'quizzes': quizzes})
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        if user_role != 'ADMIN' and course['professor_id'] != user.id:
            return Response({"error": "No tienes permisos para eliminar este curso."}, status=status.HTTP_403_FORBIDDEN)

        with connection.cursor() as cur:
            cur.execute("DELETE FROM courses WHERE id = %s", [course_id])

        return Response({"message": "Curso eliminado correctamente"}, status=status.HTTP_200_OK)


@extend_schema(
    methods=['POST'],
    summary="Añade un nuevo módulo a un curso",
    description="Permite al profesor propietario o al administrador agregar módulos curriculares.",
    responses={201: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manage_modules(request, course_id):
    user = request.user
    user_role = get_user_role(user)

    course = db.get_course_detail(course_id)
    if not course:
        return Response({"error": "Curso no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if user_role != 'ADMIN' and course['professor_id'] != user.id:
        return Response({"error": "No tienes permisos para gestionar los módulos de este curso."}, status=status.HTTP_403_FORBIDDEN)

    serializer = ModuleCreateSerializer(data={
        'course_id': course_id,
        'title': request.data.get('title'),
        'order': request.data.get('order')
    })
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    title = serializer.validated_data['title']
    order = serializer.validated_data.get('order')
    if order is not None:
        order = int(order)

    try:
        module_id = db.add_module(course_id, title, order)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    with connection.cursor() as cur:
        cur.execute("SELECT module_order FROM course_modules WHERE id = %s", [module_id])
        db_order = cur.fetchone()[0]

    return Response({
        "id": module_id,
        "title": title,
        "order": db_order,
        "message": "Módulo creado exitosamente."
    }, status=status.HTTP_201_CREATED)


@extend_schema(
    methods=['PATCH', 'PUT', 'DELETE'],
    summary="Edición y eliminación de un módulo específico",
    description="Permite al profesor propietario o al administrador editar o borrar un módulo.",
    responses={200: dict}
)
@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def module_detail(request, module_id):
    user = request.user
    user_role = get_user_role(user)

    with connection.cursor() as cur:
        cur.execute("""
            SELECT c.professor_id 
            FROM course_modules m 
            JOIN courses c ON c.id = m.course_id 
            WHERE m.id = %s
        """, [module_id])
        row = cur.fetchone()
    if not row:
        return Response({"error": "Módulo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    professor_id = row[0]
    if user_role != 'ADMIN' and professor_id != user.id:
        return Response({"error": "No tienes permisos para gestionar este módulo."}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ['PUT', 'PATCH']:
        title = request.data.get('title')
        order = request.data.get('order')
        if order is not None:
            order = int(order)
        db.update_module(module_id, title, order)
        
        with connection.cursor() as cur:
            cur.execute("SELECT title, module_order FROM course_modules WHERE id = %s", [module_id])
            title_db, order_db = cur.fetchone()
            
        return Response({
            "id": module_id,
            "title": title_db,
            "order": order_db,
            "message": "Módulo actualizado correctamente."
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        db.delete_module(module_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    methods=['POST'],
    summary="Añade una nueva lección (clase) a un módulo",
    description="Permite al profesor o admin añadir material pedagógico (PDF o Video de YouTube) con su respectiva transcripción.",
    responses={201: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manage_lessons(request, module_id):
    user = request.user
    user_role = get_user_role(user)

    with connection.cursor() as cur:
        cur.execute("""
            SELECT c.professor_id 
            FROM course_modules m 
            JOIN courses c ON c.id = m.course_id 
            WHERE m.id = %s
        """, [module_id])
        row = cur.fetchone()
    if not row:
        return Response({"error": "Módulo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    professor_id = row[0]
    if user_role != 'ADMIN' and professor_id != user.id:
        return Response({"error": "No tienes permisos para gestionar lecciones en este módulo."}, status=status.HTTP_403_FORBIDDEN)

    title = request.data.get('title')
    resource_type = request.data.get('resource_type', 'PDF')
    resource_url = request.data.get('resource_url', '')
    transcription = request.data.get('transcription', '')
    duration = request.data.get('duration', '15 minutos')
    order = request.data.get('order')
    if order is not None:
        order = int(order)

    if not title:
        return Response({"error": "El título de la lección es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)
    if resource_type not in ['PDF', 'YTB']:
        return Response({"error": "El tipo de recurso debe ser PDF o YTB (YouTube)."}, status=status.HTTP_400_BAD_REQUEST)

    lesson_id = db.add_lesson(module_id, title, duration, resource_type, resource_url, transcription, order)

    with connection.cursor() as cur:
        cur.execute("SELECT lesson_order FROM course_lessons WHERE id = %s", [lesson_id])
        db_order = cur.fetchone()[0]

    return Response({
        "id": lesson_id,
        "title": title,
        "resource_type": resource_type,
        "resource_url": resource_url,
        "transcription": transcription,
        "order": db_order,
        "message": "Lección creada exitosamente."
    }, status=status.HTTP_201_CREATED)


@extend_schema(
    methods=['PATCH', 'PUT', 'DELETE'],
    summary="Edición y eliminación de una lección específica",
    description="Permite al profesor o admin gestionar o borrar material didáctico.",
    responses={200: dict}
)
@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def lesson_detail(request, lesson_id):
    user = request.user
    user_role = get_user_role(user)

    with connection.cursor() as cur:
        cur.execute("""
            SELECT c.professor_id 
            FROM course_lessons l
            JOIN course_modules m ON m.id = l.module_id
            JOIN courses c ON c.id = m.course_id
            WHERE l.id = %s
        """, [lesson_id])
        row = cur.fetchone()
    if not row:
        return Response({"error": "Lección no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    professor_id = row[0]
    if user_role != 'ADMIN' and professor_id != user.id:
        return Response({"error": "No tienes permisos para gestionar esta lección."}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ['PUT', 'PATCH']:
        title = request.data.get('title')
        resource_type = request.data.get('resource_type')
        resource_url = request.data.get('resource_url')
        transcription = request.data.get('transcription')
        duration = request.data.get('duration')
        order = request.data.get('order')
        if order is not None:
            order = int(order)

        db.update_lesson(lesson_id, title, duration, resource_type, resource_url, transcription, order)

        with connection.cursor() as cur:
            cur.execute("""
                SELECT title, duration, resource_type, resource_url, transcription, lesson_order 
                FROM course_lessons 
                WHERE id = %s
            """, [lesson_id])
            title_db, duration_db, res_type_db, res_url_db, trans_db, order_db = cur.fetchone()

        return Response({
            "id": lesson_id,
            "title": title_db,
            "resource_type": res_type_db,
            "resource_url": res_url_db,
            "transcription": trans_db,
            "order": order_db,
            "message": "Lección actualizada correctamente."
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        db.delete_lesson(lesson_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    methods=['POST'],
    request=LessonRatingSerializer,
    summary="Completa y califica una lección del curso",
    description="Registra la finalización de una clase por el estudiante y almacena su calificación (1-5 estrellas).",
    responses={200: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_rate_lesson(request, lesson_id):
    user = request.user
    rating = request.data.get('rating')

    try:
        result = db.complete_and_rate_lesson(user.id, lesson_id, rating)
    except LessonNotFound:
        return Response({"error": "Lección no encontrada."}, status=404)
    except Exception as e:
        logger.error(f"Fallo al calificar/completar lección: {str(e)}", exc_info=True)
        return Response({"error": "Error interno al procesar progreso de lección."}, status=500)

    return Response({
        "progress_percent": result["progress_percent"],
        "is_completed": result["is_completed"],
    }, status=200)


@extend_schema(
    methods=['POST'],
    request=QuizSubmitSerializer,
    summary="Envía y evalúa las respuestas de un cuestionario",
    description="Evalúa las respuestas de opción múltiple de forma 100% segura en la base de datos.",
    responses={200: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request, module_id):
    user = request.user
    serializer = QuizSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    answers = {
        str(ans['question_index']): ans['selected_option_index']
        for ans in serializer.validated_data['answers']
    }

    try:
        result = db.submit_quiz(user.id, module_id, answers)
    except QuizNotFound:
        return Response({"error": "No se encontró el cuestionario para este módulo."}, status=404)
    except QuizEmpty:
        return Response({"error": "El cuestionario está vacío."}, status=400)
    except Exception as e:
        logger.error(f"Fallo al enviar cuestionario: {str(e)}", exc_info=True)
        return Response({"error": "Fallo al procesar el cuestionario."}, status=500)

    return Response({
        "score": result["score"],
        "passed": result["passed"],
        "global_frustration": result["global_frustration"],
        "wrong_questions_registered": result["wrong_count"],
        "message": "Cuestionario evaluado correctamente.",
    }, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_module_quiz(request, module_id):
    questions = db.get_module_quiz_for_student(module_id)
    if questions is None:
        return Response({"error": "Este módulo no tiene cuestionario."}, status=404)
    return Response(questions, status=200)


@extend_schema(
    methods=['GET'],
    summary="Estado de progreso general del alumno en un curso",
    description="Obtiene porcentaje de avance, frustración estimada, última actividad y lista de fallos pedagógicos.",
    responses={200: StudentCourseStateSerializer, 400: dict}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_course_state(request, course_id):
    try:
        state = db.get_student_course_state(request.user.id, course_id)
    except StateNotFound:
        return Response({"error": "No hay registro de progreso para este estudiante en el curso."}, status=404)
    except Exception as e:
        logger.error(f"Fallo al obtener estado del alumno: {str(e)}", exc_info=True)
        return Response({"error": "Error interno al obtener estado de progreso."}, status=500)

    return Response({
        "progress_percent": state["progress_percent"],
        "global_frustration": state["global_frustration"],
        "is_completed": state["is_completed"],
        "last_activity": state["last_activity"],
        "recent_wrong_questions": state["recent_wrong_questions"],
    }, status=200)


@extend_schema(
    methods=['GET'],
    summary="Detecta inactividad en alumnos y emite alertas de abandono",
    description="Escanea los estados de cursos inactivos por más de X días para lanzar alertas motivacionales.",
    responses={200: dict}
)
@api_view(['GET'])
@permission_classes([IsProfessorOrAdmin])
def check_inactivity_alerts(request):
    days_limit = int(request.query_params.get('days', 3))
    try:
        alerts = db.get_inactivity_alerts(days_limit)
    except Exception as e:
        logger.error(f"Fallo al verificar alertas de inactividad: {str(e)}", exc_info=True)
        return Response({"error": "Error interno al verificar inactividad."}, status=500)

    return Response({
        "inactivity_days_limit": days_limit,
        "total_alerts": len(alerts),
        "alerts": alerts,
    }, status=200)
