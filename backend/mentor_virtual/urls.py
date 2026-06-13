from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .dev_portal import developer_portal

urlpatterns = [
    # Admin Django (maneja auth.User)
    path('admin/', admin.site.urls),

    # Auth: register, login, logout
    path('api/auth/', include('users.urls')),

    # JWT refresh
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Goals: crear meta, obtener plan adaptativo
    path('api/goals/', include('goals.urls')),

    # Progress: completar pasos, registrar videos vistos
    path('api/progress/', include('progress.urls')),
    path('api/admin/',    include('adminpanel.urls')),
    path('api/tutor/',    include('tutor.urls')),
    path('api/schema/',         SpectacularAPIView.as_view(),        name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(),  name='swagger-ui'),
    path('api/schema/redoc/',   SpectacularRedocView.as_view(),      name='redoc'),
    path('api/docs/',           developer_portal,                    name='dev-portal'),
]
