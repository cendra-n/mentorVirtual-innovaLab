from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from users.views_docs import developer_portal

urlpatterns = [
    path('admin/', admin.site.urls),

    # Usuarios y auth
    path('api/auth/', include('users.urls')),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Goals, Progress, Admin, Tutor
    path('api/goals/',    include('goals.urls')),
    path('api/progress/', include('progress.urls')),
    path('api/admin/',    include('adminpanel.urls')),
    path('api/tutor/',    include('tutor.urls')),

    # Documentación
    path('api/schema/',            SpectacularAPIView.as_view(),                          name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'),     name='swagger-ui'),
    path('api/schema/redoc/',      SpectacularRedocView.as_view(url_name='schema'),       name='redoc'),
    path('api/docs/',              developer_portal,                                       name='dev-portal'),
]
