from django.urls import path
from .views import GoalCreateView, GoalListView, GoalDetailView, GoalDeleteView

urlpatterns = [
    path('',                   GoalListView.as_view(),   name='goal-list'),
    path('create/',            GoalCreateView.as_view(),  name='goal-create'),
    path('<int:goal_id>/',     GoalDetailView.as_view(),  name='goal-detail'),
    path('<int:goal_id>/delete/', GoalDeleteView.as_view(), name='goal-delete'),
]
