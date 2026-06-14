from django.urls import path
from .views import AdminUserListView, AdminUserDetailView, AdminSetPasswordView, AdminStatsView

urlpatterns = [
    path('users/',                    AdminUserListView.as_view(),    name='admin-users'),
    path('users/<int:user_id>/',      AdminUserDetailView.as_view(),  name='admin-user-detail'),
    path('users/<int:user_id>/set_password/', AdminSetPasswordView.as_view(), name='admin-set-password'),
    path('stats/',                    AdminStatsView.as_view(),        name='admin-stats'),
]
