from django.urls import path
from .views import AvailableCoursesAPIView, EnrollStudentAPIView, ListEnrollmentsAPIView

app_name = 'enrollment'

urlpatterns = [
    # Endpoint para ver la lista de cursos activos
    path('courses/available/', AvailableCoursesAPIView.as_view(), name='available-courses'),
    
    # Endpoint para ejecutar la inscripcion
    path('enroll/', EnrollStudentAPIView.as_view(), name='enroll-student'),

    #Endpoint para ver la lista de inscripciones según rol (admin or professor)
    path('enrollments/list/', ListEnrollmentsAPIView.as_view(), name='list-enrollments'),
    
]