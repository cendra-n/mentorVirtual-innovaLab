from django.urls import path
from .views import (
    CompleteStepView,
    RegisterVideoViewView,
    GoalProgressView,
    UserStreakView,
    UserLogrosView,
)

urlpatterns = [
    path('steps/<int:step_id>/complete/', CompleteStepView.as_view(),       name='complete-step'),
    path('videos/<int:video_id>/view/',   RegisterVideoViewView.as_view(),   name='video-view'),
    path('goals/<int:goal_id>/',          GoalProgressView.as_view(),        name='goal-progress'),
    path('streak/',                        UserStreakView.as_view(),           name='streak'),
    path('logros/',                        UserLogrosView.as_view(),           name='logros'),
]
