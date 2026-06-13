from django.urls import path
from .views import GoalCreateView, GoalListView, GoalDetailView

urlpatterns = [
    path('',           GoalListView.as_view(),   name='goal-list'),
    path('create/',    GoalCreateView.as_view(),  name='goal-create'),
    path('<int:goal_id>/', GoalDetailView.as_view(), name='goal-detail'),
]
