# courses/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # En Django, una misma URL puede resolver dos acciones distintas según el método HTTP:
    # GET /api/courses/ → Lista los cursos (Admin ve todos, Profe ve el suyo).
    # # POST /api/courses/ → Genera el curso de forma Manual (Flujo Nadia).
    # 1 y 2) Ruta base para LISTAR (GET) y CREAR MANUAL (POST - Flujo Nadia)
    path('', views.course_list_create, name='course-list-create'),
    
    # 3) Nueva ruta para GENERAR CON IA (POST - Flujo Gerardo)
    path('generate-with-ai/', views.generate_course_with_ai, name='generate-course-with-ai'),
    
    # 4) Rutas CRUD de Cursos, Módulos y Lecciones (Flujo Gerardo)
    path('<int:course_id>/', views.course_detail, name='course-detail'),
    path('<int:course_id>/modules/', views.manage_modules, name='manage-modules'),
    path('modules/<int:module_id>/', views.module_detail, name='module-detail'),
    path('modules/<int:module_id>/lessons/', views.manage_lessons, name='manage-lessons'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson-detail'),
    
    # 5) Rutas de Progreso, Cuestionarios y Alertas (Flujo Gerardo)
    path('lessons/<int:lesson_id>/complete-rate/', views.complete_rate_lesson, name='complete-rate-lesson'),
    path('modules/<int:module_id>/quiz-submit/', views.submit_quiz, name='submit-quiz'),
    path('modules/<int:module_id>/quiz/', views.get_module_quiz, name='get-module-quiz'),
    path('<int:course_id>/student-state/', views.student_course_state, name='student-course-state'),
    path('alerts/inactivity/', views.check_inactivity_alerts, name='check-inactivity-alerts'),
]