from django.urls import path
from .views import (
    api_login, api_register, api_logout,
    api_profile, api_change_password, api_users_list, api_update_student_profile
)
from .views_geo import CountryListView, ProvinceListView, AssociateProvinceView, LocalityListView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/',           api_login,           name='api_login'),
    path('register/',        api_register,        name='api_register'),
    path('logout/',          api_logout,          name='api_logout'),
    path('me/',              api_profile,         name='api_profile'),
    path('change_password/', api_change_password, name='change-password'),
    path('users/',           api_users_list,      name='api_users_list'),
    path('token/refresh/',   TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/student/update/', api_update_student_profile, name='update-student-profile'),
    path('geo/countries/', CountryListView.as_view(), name='geo-countries'),
    path('geo/provinces/', AssociateProvinceView.as_view(), name='geo-provinces'),
    path('geo/provinces/list', ProvinceListView.as_view(), name='geo-provinces-list'),
    path('geo/localities/', LocalityListView.as_view(), name='geo-localities'),
]
