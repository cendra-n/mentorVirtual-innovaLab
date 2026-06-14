import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema, inline_serializer

from .db import (
    sp_complete_step, sp_get_user_progress, sp_register_video_view,
    sp_get_viewed_videos, sp_update_streak, sp_get_streak,
)
from goals.db import sp_unlock_logro_if_eligible, sp_get_user_logros

logger = logging.getLogger(__name__)


class CompleteStepView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Marcar paso como completado",
        request=inline_serializer('CompleteStepRequest', fields={
            'goal_id': serializers.IntegerField(help_text='ID de la meta a la que pertenece el paso'),
        }),

    )
    def post(self, request, step_id: int):
        goal_id = request.data.get('goal_id')
        if not goal_id:
            return Response({'error': 'goal_id es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

        user_id     = request.user.id
        step_result = sp_complete_step(step_id, user_id)
        streak      = sp_update_streak(user_id)
        new_logros  = sp_unlock_logro_if_eligible(goal_id, user_id)
        progress    = sp_get_user_progress(user_id, goal_id)

        return Response({'step': step_result, 'progress': progress, 'streak': streak, 'new_logros': new_logros})


class RegisterVideoViewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Registrar video visto",
        request=inline_serializer('VideoViewRequest', fields={
            'step_id': serializers.IntegerField(help_text='ID del paso al que pertenece el video'),
        }),
    )
    def post(self, request, video_id: int):
        step_id = request.data.get('step_id')
        if not step_id:
            return Response({'error': 'step_id es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.id
        result  = sp_register_video_view(user_id, video_id, step_id)
        streak  = sp_update_streak(user_id)
        return Response({'video_view': result, 'streak': streak})


class GoalProgressView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Progreso del usuario en una meta")
    def get(self, request, goal_id: int):
        user_id  = request.user.id
        progress = sp_get_user_progress(user_id, goal_id)
        if not progress:
            return Response({'error': 'Meta no encontrada o sin progreso.'}, status=status.HTTP_404_NOT_FOUND)
        viewed_videos = sp_get_viewed_videos(user_id, goal_id)
        return Response({'progress': progress, 'viewed_videos': viewed_videos})


class UserStreakView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Racha de días activos del usuario")
    def get(self, request):
        return Response(sp_get_streak(request.user.id))


class UserLogrosView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Logros del usuario (desbloqueados y pendientes)")
    def get(self, request):
        return Response({'logros': sp_get_user_logros(request.user.id)})
