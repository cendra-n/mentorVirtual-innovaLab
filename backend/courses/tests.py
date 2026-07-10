from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import UserProfile, ProfessorProfile
from .models import Course
from courses import db

class CourseAPITests(APITestCase):
                                        
    def setUp(self):
        # 1. Creamos los grupos requeridos por el sistema
        self.admin_group, _ = Group.objects.get_or_create(name='ADMIN')
        self.professor_group, _ = Group.objects.get_or_create(name='PROFESSOR')

        # 2. El Admin
        self.admin_user = User.objects.create_superuser(
            username='admin_1', 
            email='admin@test.com',
            password='Password123'
        )
        self.admin_user.groups.add(self.admin_group)
        UserProfile.objects.update_or_create(user=self.admin_user, defaults={'role': 'ADMIN'})
        
       # 3. El Profesor Carlos
        self.professor_user = User.objects.create_user(
            username='carlos sanches', 
            email='carlos@test.com',
            password='Password123'
        )
        self.professor_user.groups.add(self.professor_group)
        user_prof_carlos, _ = UserProfile.objects.update_or_create(user=self.professor_user, defaults={'role': 'PROFESSOR'})
        # Forzamos la propiedad simulando el related_name esperado por tu propiedad is_professor
        self.professor_user.profile = user_prof_carlos 
        
        ProfessorProfile.objects.update_or_create(
            user=self.professor_user,
            defaults={
                'dni': '11111111',
                'address': 'Calle Falsa 123'
            }
        )

        # 4. El Profesor Gerardo
        self.other_professor = User.objects.create_user(
            username='gerardo lopez',
            email='gerardo@test.com',
            password='Password123'
        )
        self.other_professor.groups.add(self.professor_group)
        user_prof_gerardo, _ = UserProfile.objects.update_or_create(user=self.other_professor, defaults={'role': 'PROFESSOR'})
        # Forzamos también para Gerardo
        self.other_professor.profile = user_prof_gerardo
        
        ProfessorProfile.objects.update_or_create(
            user=self.other_professor,
            defaults={
                'dni': '22222222',
                'address': 'Calle Falsa 456'
            }
        )

        # URLs del módulo
        self.url_listar_cursos = '/api/courses/'               
        self.url_crear_manual = '/api/courses/'                
        self.url_generar_ia = '/api/courses/generate-with-ai/' 

        # Datos nuevos agregados en course
        self.valid_course_data = {
            "title": "Ciberseguridad",
            "description": "Lo que hay en el curso.",
            "level": "medio",
            "discipline": "informatica",
            "objectives": "Lo que logra el alumno haciendo esto",
            "modules": [
                {
                    "title": "Módulo Introductorio",
                    "order": 1,
                    "lessons": [
                        {
                            "title": "Introducción a la Ciberseguridad",
                            "duration": "15 minutos",
                            "resource_type": "PDF",
                            "resource_url": "http://example.com/material.pdf",
                            "transcription": "Texto de prueba",
                            "order": 1
                        }
                    ]
                }
            ]
        }

    # =========================================================================
    # 1) TEST PARA EL MÉTODO GET (LISTAR)
    # =========================================================================
    def test_get_courses_as_professor(self):
        """ Un profesor solo debe ver sus propios cursos, no los de los demás """
        Course.objects.create(
            title="Curso Carlos", description="Desc", level="medio", 
            discipline="it", objectives="obj", professor=self.professor_user, is_active=True
        )
        Course.objects.create(
            title="Curso Gerardo", description="Desc", level="medio", 
            discipline="it", objectives="obj", professor=self.other_professor, is_active=True
        )

        # Autenticamos como el profesor Carlos
        self.client.force_authenticate(user=self.professor_user)
        response = self.client.get(self.url_listar_cursos)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debería ver solo 1 curso (el suyo) según tu filtro de views.py
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Curso Carlos")

    # =========================================================================
    # 2) TEST PARA EL MÉTODO POST MANUAL (FLUJO NADIA)
    # =========================================================================
    def test_create_course_manual_success(self):
        """ Flujo Manual: Profesor crea curso con datos del cuaderno e INACTIVO """
        self.client.force_authenticate(user=self.professor_user)
        response = self.client.post(self.url_crear_manual, self.valid_course_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Ciberseguridad")
        self.assertEqual(response.data['id_user'], self.professor_user.id)
        self.assertEqual(response.data['professor'], "carlos sanches")  # El username real esperado
        self.assertFalse(response.data['is_active'])

    def test_create_course_mvp_restriction(self):
        """ Restricción MVP: Rebota si el profesor ya tiene 2 cursos """
        Course.objects.create(
            title="Curso Activo Previo 1", description="Desc", level="alto", 
            discipline="it", objectives="obj", professor=self.professor_user, is_active=True
        )
        Course.objects.create(
            title="Curso Activo Previo 2", description="Desc", level="alto", 
            discipline="it", objectives="obj", professor=self.professor_user, is_active=True
        )

        self.client.force_authenticate(user=self.professor_user)
        response = self.client.post(self.url_crear_manual, self.valid_course_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Un profesor solo puede tener un máximo de 2 cursos a la vez.")


    def test_create_course_manual_with_modules_and_lessons(self):
        """ Valida la creación manual de curso con módulos y lecciones aninados """
        self.client.force_authenticate(user=self.professor_user)
        
        nested_data = {
            **self.valid_course_data,
            "modules": [
                {
                    "title": "Módulo de Prueba Manual",
                    "order": 1,
                    "lessons": [
                        {
                            "title": "Lección de Texto",
                            "duration": "10 minutos",
                            "resource_type": "PDF",
                            "resource_url": "http://example.com/material.pdf",
                            "transcription": "Texto completo lección.",
                            "order": 1
                        },
                        {
                            "title": "Lección de Video",
                            "duration": "15 minutos",
                            "resource_type": "YTB",
                            "resource_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "transcription": "Transcripción video.",
                            "order": 2
                        }
                    ]
                }
            ]
        }
        
        response = self.client.post(self.url_crear_manual, nested_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar la base de datos
        course = Course.objects.get(id=response.data['id'])
        self.assertEqual(course.title, "Ciberseguridad")
        self.assertEqual(course.modules.count(), 1)
        
        module = course.modules.first()
        self.assertEqual(module.title, "Módulo de Prueba Manual")
        self.assertEqual(module.lessons.count(), 2)
        
        pdf_lesson = module.lessons.get(resource_type='PDF')
        self.assertEqual(pdf_lesson.title, "Lección de Texto")
        self.assertEqual(pdf_lesson.resource_url, "http://example.com/material.pdf")
        
        yt_lesson = module.lessons.get(resource_type='YTB')
        self.assertEqual(yt_lesson.title, "Lección de Video")
        self.assertEqual(yt_lesson.resource_url, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_create_course_manual_with_quiz(self):
        """ Valida la creación manual de curso con un cuestionario y su recuperación en el GET detail """
        from django.conf import settings
        import os
        self.client.force_authenticate(user=self.professor_user)
        
        nested_data = {
            **self.valid_course_data,
            "modules": [
                {
                    "title": "Módulo de Prueba Manual con Cuestionario",
                    "order": 1,
                    "lessons": [
                        {
                            "title": "Lección de Texto",
                            "duration": "10 minutos",
                            "resource_type": "PDF",
                            "resource_url": "http://example.com/material.pdf",
                            "transcription": "Texto completo lección.",
                            "order": 1
                        }
                    ],
                    "quiz": [
                        {
                            "question": "¿De qué color es el caballo blanco de San Martín?",
                            "options": ["Blanco", "Negro", "Marrón", "Gris"],
                            "correct_option_index": 0
                        },
                        {
                            "question": "¿Cuántas patas tiene un perro?",
                            "options": ["Dos", "Tres", "Cuatro", "Cinco"],
                            "correct_option_index": 2
                        }
                    ]
                }
            ]
        }
        
        response = self.client.post(self.url_crear_manual, nested_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        course_id = response.data['id']
        
        # Consultamos el detalle del curso
        url_detalle = f'/api/courses/{course_id}/'
        response_detail = self.client.get(url_detalle)
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
        
        # Comprobar que el cuestionario se cargó correctamente en la respuesta
        modules = response_detail.data.get('modules', [])
        self.assertEqual(len(modules), 1)
        
        quiz = modules[0].get('quiz', [])
        self.assertEqual(len(quiz), 2)
        self.assertEqual(quiz[0]['question'], "¿De qué color es el caballo blanco de San Martín?")
        self.assertEqual(quiz[0]['correct_option_index'], 0)
        self.assertEqual(quiz[1]['question'], "¿Cuántas patas tiene un perro?")
        self.assertEqual(quiz[1]['correct_option_index'], 2)
        
        # Limpieza de archivos creados en el test
        course = Course.objects.get(id=course_id)
        for m in course.modules.all():
            media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
            quiz_file_path = os.path.join(media_root, 'courses', f"quiz_modulo_{m.id}.json")
            if os.path.exists(quiz_file_path):
                os.remove(quiz_file_path)

    def test_update_course_nested_modules_and_lessons_success(self):
        """ Valida la actualización y reconciliación de curso con módulos, lecciones y cuestionarios """
        from django.conf import settings
        import os
        self.client.force_authenticate(user=self.professor_user)
        
        # 1. Crear el curso inicialmente
        create_response = self.client.post(self.url_crear_manual, self.valid_course_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        course_id = create_response.data['id']
        
        course = Course.objects.get(id=course_id)
        original_module = course.modules.first()
        original_lesson = original_module.lessons.first()
        
        # 2. Preparar datos de actualización (PATCH) con reconciliación
        update_data = {
            "title": "Ciberseguridad Avanzada",
            "description": "Edición avanzada del curso.",
            "level": "medio",
            "discipline": "informatica",
            "objectives": "Objetivos actualizados",
            "modules": [
                {
                    "id": original_module.id,
                    "title": "Módulo Introductorio Modificado",
                    "order": 1,
                    "lessons": [
                        {
                            "id": original_lesson.id,
                            "title": "Introducción a la Ciberseguridad Modificada",
                            "duration": "20 minutos",
                            "resource_type": "PDF",
                            "resource_url": "http://example.com/material_modificado.pdf",
                            "transcription": "Texto modificado",
                            "order": 1
                        },
                        {
                            "title": "Nueva Clase Añadida",
                            "duration": "10 minutos",
                            "resource_type": "YTB",
                            "resource_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "transcription": "Video nuevo",
                            "order": 2
                        }
                    ]
                },
                {
                    "title": "Módulo Nuevo de Cuestionario",
                    "order": 2,
                    "lessons": [
                        {
                            "title": "Clase Única de Módulo Nuevo",
                            "duration": "15 minutos",
                            "resource_type": "PDF",
                            "resource_url": "http://example.com/nuevo_modulo.pdf",
                            "transcription": "Texto nuevo",
                            "order": 1
                        }
                    ],
                    "quiz": [
                        {
                            "question": "¿De qué color es la manzana roja?",
                            "options": ["Roja", "Verde", "Azul"],
                            "correct_option_index": 0
                        },
                        {
                            "question": "¿Cuánto es 2+2?",
                            "options": ["3", "4", "5"],
                            "correct_option_index": 1
                        }
                    ]
                }
            ]
        }
        
        url_detalle = f'/api/courses/{course_id}/'
        response_update = self.client.patch(url_detalle, update_data, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        
        # 3. Validar cambios en Base de Datos
        course.refresh_from_db()
        self.assertEqual(course.title, "Ciberseguridad Avanzada")
        self.assertEqual(course.modules.count(), 2)
        
        # Verificar primer módulo y lecciones
        mod1 = course.modules.get(id=original_module.id)
        self.assertEqual(mod1.title, "Módulo Introductorio Modificado")
        self.assertEqual(mod1.lessons.count(), 2)
        
        l1 = mod1.lessons.get(id=original_lesson.id)
        self.assertEqual(l1.title, "Introducción a la Ciberseguridad Modificada")
        self.assertEqual(l1.resource_url, "http://example.com/material_modificado.pdf")
        
        l2 = mod1.lessons.exclude(id=original_lesson.id).first()
        self.assertEqual(l2.title, "Nueva Clase Añadida")
        self.assertEqual(l2.resource_type, "YTB")
        
        # Verificar segundo módulo y quiz
        mod2 = course.modules.exclude(id=original_module.id).first()
        self.assertEqual(mod2.title, "Módulo Nuevo de Cuestionario")
        self.assertEqual(mod2.lessons.count(), 1)
        
        # Verificar que el cuestionario se guardó en la base de datos
        from django.db import connection
        with connection.cursor() as cur:
            cur.execute("SELECT EXISTS(SELECT 1 FROM module_quiz WHERE module_id = %s)", [mod2.id])
            quiz_exists = cur.fetchone()[0]
        self.assertTrue(quiz_exists)
        
        # Comprobar que en el GET detail retorna los cuestionarios
        response_detail = self.client.get(url_detalle)
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
        detail_modules = response_detail.data.get('modules', [])
        
        mod2_detail = [m for m in detail_modules if m['id'] == mod2.id][0]
        self.assertEqual(len(mod2_detail.get('quiz', [])), 2)
        
        # Limpieza
        pass

    def test_delete_course_as_owner(self):
        course = Course.objects.create(
            title="Curso de Carlos", description="Desc", level="medio", 
            discipline="it", objectives="obj", professor=self.professor_user, is_active=True
        )
        self.client.force_authenticate(user=self.professor_user)
        url_detalle = f'/api/courses/{course.id}/'
        
        response = self.client.delete(url_detalle)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=course.id).exists())

    def test_delete_course_as_other_professor_forbidden(self):
        """ Un profesor no puede eliminar el curso de otro profesor """
        course = Course.objects.create(
            title="Curso de Carlos", description="Desc", level="medio", 
            discipline="it", objectives="obj", professor=self.professor_user, is_active=True
        )
        self.client.force_authenticate(user=self.other_professor)
        url_detalle = f'/api/courses/{course.id}/'
        
        response = self.client.delete(url_detalle)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Course.objects.filter(id=course.id).exists())


    # =========================================================================
    # 3) TEST PARA EL MÉTODO POST CON IA (FLUJO GERARDO)
    # =========================================================================    
    def test_generate_course_with_ai_success(self):
        """ Valida la generación exitosa de un curso con IA y la persistencia de módulos/lecciones """
        from unittest.mock import patch
        
        mock_ai_response = {
            "title": "Celulares para Abuelos",
            "description": "Aprende a usar tu smartphone sin complicaciones.",
            "level": "beginner",
            "discipline": "Tecnología",
            "objectives": "Aprender a mandar audios y llamadas.",
            "modules": [
                {
                    "title": "Módulo 1: WhatsApp básico",
                    "youtube_query": "usar whatsapp adultos mayores",
                    "pdf_title": "Guía de WhatsApp",
                    "pdf_content": "Para enviar un mensaje, abre la aplicación...",
                    "quiz": [
                        {
                            "question": "¿Cuál es el icono de WhatsApp?",
                            "options": ["Un teléfono verde", "Una F azul", "Una cámara", "Un pájaro"],
                            "correct_option_index": 0
                        }
                    ]
                }
            ]
        }
        
        mock_yt_response = {
            "video_id": "12345",
            "title": "Tutorial WhatsApp Sencillo",
            "thumbnail": "https://img.yt.com/1.jpg",
            "url": "https://www.youtube.com/watch?v=12345",
            "channel": "Canal Abuelos"
        }

        self.client.force_authenticate(user=self.professor_user)
        
        with patch('courses.services.AnthropicService.generate_course_structure', return_value=mock_ai_response) as mock_ai, \
             patch('courses.services.YouTubeService.search_course_video', return_value=mock_yt_response) as mock_yt:
             
            post_data = {
                "objetivo_curso": "Aprender a usar el celular para abuelos",
                "cantidad_modulos": 1,
                "generar_pdfs": True,
                "generar_cuestionarios": True
            }
            
            response = self.client.post(self.url_generar_ia, post_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['title'], "Celulares para Abuelos")
            self.assertFalse(response.data['is_active']) # Borrador
            self.assertEqual(len(response.data['modules']), 1)
            
            # Verificar que el curso se guardó en la BD
            course_db = Course.objects.get(id=response.data['id'])
            self.assertEqual(course_db.title, "Celulares para Abuelos")
            self.assertEqual(course_db.professor, self.professor_user)
            
            # Verificar módulos y lecciones en BD
            self.assertEqual(course_db.modules.count(), 1)
            module_db = course_db.modules.first()
            self.assertEqual(module_db.title, "Módulo 1: WhatsApp básico")
            
            # 2 Lecciones creadas: 1 Video + 1 PDF
            self.assertEqual(module_db.lessons.count(), 2)
            
            yt_lesson = module_db.lessons.filter(resource_type='YTB').first()
            self.assertIsNotNone(yt_lesson)
            self.assertEqual(yt_lesson.resource_url, "https://www.youtube.com/watch?v=12345")
            
            pdf_lesson = module_db.lessons.filter(resource_type='PDF').first()
            self.assertIsNotNone(pdf_lesson)
            self.assertTrue(pdf_lesson.resource_url.endswith(".pdf"))

            # Verificar que el cuestionario esté en la respuesta
            self.assertEqual(len(response.data['modules'][0]['quiz']), 1)
            self.assertEqual(response.data['modules'][0]['quiz'][0]['question'], "¿Cuál es el icono de WhatsApp?")

    def test_generate_course_with_ai_validation_error(self):
        """ Valida que el endpoint rebote si los parámetros obligatorios no son provistos """
        self.client.force_authenticate(user=self.professor_user)
        
        # Enviamos datos vacíos
        response = self.client.post(self.url_generar_ia, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("objetivo_curso", response.data)

#Comentar esta linea ya que: En las pruebas unitarias está terminantemente prohibido hacer llamadas a APIs reales (es una mala práctica severa).
#  Se deben usar mocks (falsificaciones con Mockito/Unittest) para simular la respuesta de Anthropic

    # def test_generate_course_with_ai_mvp_restriction(self):
    #     """ Valida que no se pueda generar un curso por IA si el profesor ya tiene 2 cursos """
    #     # Creamos 2 cursos previos
    #     Course.objects.create(
    #         title="Curso Previo 1", description="Desc", level="beginner", 
    #         discipline="it", objectives="obj", professor=self.professor_user, is_active=False
    #     )
    #     Course.objects.create(
    #         title="Curso Previo 2", description="Desc", level="beginner", 
    #         discipline="it", objectives="obj", professor=self.professor_user, is_active=False
    #     )
        
    #     self.client.force_authenticate(user=self.professor_user)
        
    #     post_data = {
    #         "objetivo_curso": "Aprender a usar el celular para abuelos",
    #         "cantidad_modulos": 1,
    #         "generar_pdfs": True,
    #         "generar_cuestionarios": True
    #     }
        
    #     response = self.client.post(self.url_generar_ia, post_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data["error"], "Un profesor solo puede tener un máximo de 2 cursos a la vez.")

    def test_complete_rate_lesson(self):
        """ Valida completar y calificar una lección, y el cálculo de progreso y tiempo de duración """
        from .models import Module, Lesson, LessonProgress, StudentCourseState
        
        course = Course.objects.create(
            title="Curso Test", description="Desc", level="beginner", 
            discipline="it", objectives="obj", professor=self.professor_user, is_active=True
        )
        module = Module.objects.create(course=course, title="Módulo 1", order=1)
        lesson1 = Lesson.objects.create(module=module, title="Clase 1", resource_type="YTB", order=1)
        lesson2 = Lesson.objects.create(module=module, title="Clase 2", resource_type="PDF", order=2)
        
        self.client.force_authenticate(user=self.other_professor)
        
        # Completar la primera clase
        response = self.client.post(f"/api/courses/lessons/{lesson1.id}/complete-rate/", {"rating": 5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress_percent'], 50.0)
        self.assertFalse(response.data['is_completed'])
        
        progress = LessonProgress.objects.get(student=self.other_professor, lesson=lesson1)
        self.assertTrue(progress.is_completed)
        self.assertEqual(progress.rating, 5)
        
        # Completar la segunda clase (finalizar curso)
        response = self.client.post(f"/api/courses/lessons/{lesson2.id}/complete-rate/", {"rating": 4}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress_percent'], 100.0)
        self.assertTrue(response.data['is_completed'])
        
        state = StudentCourseState.objects.get(student=self.other_professor, course=course)
        self.assertTrue(state.is_completed)
        self.assertIsNotNone(state.total_time_spent)

    def test_submit_quiz_and_frustration_tracking(self):
        """ Valida la evaluación de cuestionarios, almacenamiento de preguntas erradas e incremento de frustración """
        import json
        import os
        from django.conf import settings
        from .models import Module, StudentCourseState, WrongQuestion
        
        course = Course.objects.create(
            title="Curso Test", description="Desc", level="beginner", 
            discipline="it", objectives="obj", professor=self.professor_user, is_active=True
        )
        module = Module.objects.create(course=course, title="Módulo 1", order=1)
        
        media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
        courses_media_dir = os.path.join(media_root, 'courses')
        os.makedirs(courses_media_dir, exist_ok=True)
        
        quiz_data = [
            {
                "question": "¿De qué color es el cielo?",
                "options": ["Azul", "Rojo", "Verde", "Amarillo"],
                "correct_option_index": 0
            }
        ]
        
        quiz_file_path = ""
        db.save_module_quiz(module.id, quiz_data)
            
        self.client.force_authenticate(user=self.other_professor)
        
        post_data = {
            "answers": [
                {"question_index": 0, "selected_option_index": 1}
            ]
        }
        response = self.client.post(f"/api/courses/modules/{module.id}/quiz-submit/", post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['passed'])
        self.assertEqual(response.data['global_frustration'], 1)
        self.assertEqual(response.data['wrong_questions_registered'], 1)
        
        self.assertEqual(WrongQuestion.objects.count(), 1)
        wq = WrongQuestion.objects.first()
        self.assertEqual(wq.selected_option, "Rojo")
        self.assertEqual(wq.correct_option, "Azul")
        
        post_data_correct = {
            "answers": [
                {"question_index": 0, "selected_option_index": 0}
            ]
        }
        response = self.client.post(f"/api/courses/modules/{module.id}/quiz-submit/", post_data_correct, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['passed'])
        self.assertEqual(response.data['global_frustration'], 0)
        
        if os.path.exists(quiz_file_path):
            os.remove(quiz_file_path)

    def test_check_inactivity_alerts(self):
        """ Valida que el escáner de inactividad detecte alumnos inactivos y emita alertas """
        from django.utils import timezone
        from datetime import timedelta
        from .models import StudentCourseState
        
        course = Course.objects.create(
            title="Curso Test", description="Desc", level="beginner", 
            discipline="it", objectives="obj", professor=self.professor_user, is_active=True
        )
        
        state = StudentCourseState.objects.create(
            student=self.other_professor,
            course=course,
            progress_percent=10.0,
            is_completed=False
        )
        
        StudentCourseState.objects.filter(id=state.id).update(
            last_activity=timezone.now() - timedelta(days=4)
        )
        
        # Asignamos el perfil al admin en los tests para evitar el error de relación diferida en la caché de Django
        admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin_user, defaults={'role': 'ADMIN'})
        self.admin_user.profile = admin_profile
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get("/api/courses/alerts/inactivity/?days=3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_alerts'], 1)
        self.assertEqual(response.data['alerts'][0]['student_username'], self.other_professor.username)
        
        state.refresh_from_db()
        self.assertTrue(state.inactivity_alert_sent)

    def test_student_course_visibility_and_admin_activation(self):
        """ Valida que los estudiantes sólo vean cursos activos, y que sólo el Admin pueda activar/desactivar """
        from .models import StudentCourseState
        
        # 1. Crear curso inactivo
        course = Course.objects.create(
            title="Curso Borrador", description="Desc", level="beginner", 
            discipline="it", objectives="obj", professor=self.professor_user, is_active=False
        )
        
        # Crear un usuario Alumno
        student_user = User.objects.create_user(
            username='alumno.test', email='alumno@test.com', password='Password123'
        )
        UserProfile.objects.update_or_create(user=student_user, defaults={'role': 'STUDENT'})
        
        # El alumno intenta listar cursos -> Debe recibir lista vacía (porque está inactivo)
        self.client.force_authenticate(user=student_user)
        response = self.client.get(self.url_listar_cursos)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
        # El alumno intenta ver el detalle directamente -> 403 Forbidden
        response = self.client.get(f"/api/courses/{course.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 2. El profesor intenta activar su propio curso -> 400 Bad Request
        self.client.force_authenticate(user=self.professor_user)
        response = self.client.patch(f"/api/courses/{course.id}/", {"is_active": True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        
        # 3. El Admin activa el curso -> 200 OK
        admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin_user, defaults={'role': 'ADMIN'})
        self.admin_user.profile = admin_profile
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(f"/api/courses/{course.id}/", {"is_active": True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_active'])
        
        # 4. Ahora el alumno sí puede ver el curso
        self.client.force_authenticate(user=student_user)
        response = self.client.get(self.url_listar_cursos)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Curso Borrador")
        
        response = self.client.get(f"/api/courses/{course.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_professor_crud_modules_and_lessons(self):
        """ Valida que el profesor propietario pueda gestionar módulos y lecciones de su curso """
        from .models import Module, Lesson
        
        course = Course.objects.create(
            title="Curso Carlos", description="Desc", level="beginner", 
            discipline="it", objectives="obj", professor=self.professor_user, is_active=False
        )
        
        # 1. Crear un Módulo
        self.client.force_authenticate(user=self.professor_user)
        response = self.client.post(f"/api/courses/{course.id}/modules/", {"title": "Módulo Temático 1"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        module_id = response.data['id']
        
        # 2. Crear una Lección dentro de ese módulo con transcripción
        lesson_data = {
            "title": "Clase Interactiva 1",
            "resource_type": "YTB",
            "resource_url": "https://www.youtube.com/watch?v=hello",
            "transcription": "Bienvenidos a la clase número uno...",
            "duration": "12 minutos"
        }
        response = self.client.post(f"/api/courses/modules/{module_id}/lessons/", lesson_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        lesson_id = response.data['id']
        self.assertEqual(response.data['transcription'], "Bienvenidos a la clase número uno...")
        
        # 3. Editar la lección
        response = self.client.patch(f"/api/courses/lessons/{lesson_id}/", {"title": "Clase Modificada", "transcription": "Nueva transcripción"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Clase Modificada")
        self.assertEqual(response.data['transcription'], "Nueva transcripción")
        
        # 4. Intentar que otro profesor edite o borre -> 403 Forbidden
        self.client.force_authenticate(user=self.other_professor)
        response = self.client.delete(f"/api/courses/lessons/{lesson_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 5. El propietario sí puede borrar
        self.client.force_authenticate(user=self.professor_user)
        response = self.client.delete(f"/api/courses/lessons/{lesson_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=lesson_id).exists())

    def test_student_course_weighted_progress_calculation(self):
        """ Valida el cálculo de progreso general usando ponderaciones (PDF: 30%, YTB: 30%, Quiz: 40%) """
        from .models import Module, Lesson, StudentCourseState, LessonProgress
        from django.conf import settings
        import os
        import json
        
        # 1. Configurar datos del curso
        course = Course.objects.create(
            title="Curso de Finanzas", description="Desc", level="beginner",
            discipline="finanzas", objectives="obj", professor=self.professor_user, is_active=True
        )
        module = Module.objects.create(course=course, title="Módulo 1", order=1)
        
        pdf_lesson = Lesson.objects.create(module=module, title="Lectura PDF", resource_type='PDF', order=1)
        ytb_lesson = Lesson.objects.create(module=module, title="Video Youtube", resource_type='YTB', order=2)
        
        quiz_data = [
            {
                "question": "¿Cuánto es 2+2?",
                "options": ["3", "4", "5"],
                "correct_option_index": 1
            },
            {
                "question": "¿De qué color es el cielo?",
                "options": ["Azul", "Rojo", "Verde"],
                "correct_option_index": 0
            }
        ]
        quiz_file_path = ""
        db.save_module_quiz(module.id, quiz_data)
            
        # Forzar autenticación de estudiante
        student = self.other_professor # Usar el otro usuario como alumno para simplificar
        self.client.force_authenticate(user=student)
        
        # 2. Completar lectura PDF -> Debe dar 30% de progreso (w_pdf = 30%)
        response = self.client.post(f"/api/courses/lessons/{pdf_lesson.id}/complete-rate/", {"rating": 5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress_percent'], 30.0)
        self.assertFalse(response.data['is_completed'])
        
        # 3. Completar video YTB -> Debe sumar otros 30%, llegando a 60% de progreso total
        response = self.client.post(f"/api/courses/lessons/{ytb_lesson.id}/complete-rate/", {"rating": 4}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress_percent'], 60.0)
        self.assertFalse(response.data['is_completed'])
        
        # 4. Enviar Cuestionario con 1 respuesta correcta (50% de score) -> Debe sumar 20% (0.4 * 0.5), totalizando 80%
        quiz_submit_data_50 = {
            "answers": [
                {"question_index": 0, "selected_option_index": 1},  # Correcta (4)
                {"question_index": 1, "selected_option_index": 1}   # Incorrecta
            ]
        }
        response = self.client.post(f"/api/courses/modules/{module.id}/quiz-submit/", quiz_submit_data_50, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 50.0)
        
        state = StudentCourseState.objects.get(student=student, course=course)
        self.assertEqual(state.progress_percent, 80.0)
        self.assertFalse(state.is_completed)
        
        # 5. Enviar Cuestionario con 2 respuestas correctas (100% de score) -> Debe sumar los 40% del quiz, llegando a 100%
        quiz_submit_data_100 = {
            "answers": [
                {"question_index": 0, "selected_option_index": 1},  # Correcta
                {"question_index": 1, "selected_option_index": 0}   # Correcta (Azul)
            ]
        }
        response = self.client.post(f"/api/courses/modules/{module.id}/quiz-submit/", quiz_submit_data_100, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 100.0)
        
        state.refresh_from_db()
        self.assertEqual(state.progress_percent, 100.0)
        self.assertTrue(state.is_completed)
        self.assertIsNotNone(state.completed_at)
        
        # Limpieza
        if os.path.exists(quiz_file_path):
            os.remove(quiz_file_path)