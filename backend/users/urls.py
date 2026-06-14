from django.urls import path
from .views import api_login, api_register, api_logout, api_profile, api_users_list

urlpatterns = [
    path('login/', api_login, name='api_login'),
    path('register/', api_register, name='api_register'),
    path('logout/', api_logout, name='api_logout'),
    path('profile/', api_profile, name='api_profile'),
    path('users/', api_users_list, name='api_users_list'),
]