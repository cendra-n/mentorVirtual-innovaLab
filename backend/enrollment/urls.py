from django.urls import path
from enrollment.views import AvailableCoursesAPIView, EnrollStudentAPIView, StudentDashboardAPIView

app_name = 'enrollment'

urlpatterns = [
    # Endpoint para ver la lista de cursos activos
    path('courses/available/', AvailableCoursesAPIView.as_view(), name='available-courses'),
    
    # Endpoint para ejecutar la inscripcion
    path('enroll/', EnrollStudentAPIView.as_view(), name='enroll-student'),
    
    # Endpoint para ver el panel del alumno con sus cursos y profesores
    path('dashboard/', StudentDashboardAPIView.as_view(), name='student-dashboard'),
]