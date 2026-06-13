import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema, OpenApiExample, inline_serializer

from .db import (
    sp_get_goal_by_user_and_text, sp_create_goal, sp_get_goals_by_user,
    sp_get_goal_detail, sp_create_step, sp_get_steps_by_goal,
    sp_save_video, sp_get_videos_by_step, sp_create_logro,
    sp_get_logros_by_goal,
)
from .services import generate_plan_with_claude, search_youtube_video

logger = logging.getLogger(__name__)


def _build_full_plan(goal: dict, user_id: int) -> dict:
    goal_id = goal['id']
    steps   = sp_get_steps_by_goal(goal_id, user_id)
    for step in steps:
        step['videos'] = sp_get_videos_by_step(step['id'])
    logros = sp_get_logros_by_goal(goal_id)
    return {'goal': goal, 'steps': steps, 'logros': logros}


class GoalCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Crear meta y generar plan con IA",
        description="Recibe una meta en lenguaje libre, genera un plan personalizado con Claude API y busca videos en YouTube para cada paso.",
        request=inline_serializer('GoalCreateRequest', fields={
            'goal_text': serializers.CharField(help_text='Meta en lenguaje libre. Ej: quiero aprender a usar la computadora'),
        }),
        examples=[OpenApiExample('Ejemplo', value={'goal_text': 'quiero aprender a usar la computadora para buscar trabajo'})],
    )
    def post(self, request):
        goal_text = request.data.get('goal_text', '').strip()
        if not goal_text:
            return Response({'error': 'goal_text es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.id
        existing = sp_get_goal_by_user_and_text(user_id, goal_text)
        if existing:
            return Response(_build_full_plan(existing, user_id))

        try:
            plan = generate_plan_with_claude(goal_text)
        except Exception as exc:
            logger.error("Error Claude API: %s", exc)
            return Response({'error': 'No se pudo generar el plan. Intentá de nuevo.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        goal_id = sp_create_goal(user_id, goal_text)
        goal    = sp_get_goal_detail(goal_id, user_id)

        for step_data in plan.get('steps', []):
            step_id = sp_create_step(
                goal_id=goal_id,
                order=step_data['order'],
                title=step_data['title'],
                description=step_data['description'],
                youtube_query=step_data.get('youtube_query', step_data['title']),
            )
            video = search_youtube_video(step_data.get('youtube_query', step_data['title']))
            if video:
                sp_save_video(step_id=step_id, video_id=video['video_id'], title=video['title'],
                              thumbnail=video['thumbnail'], url=video['url'], channel=video['channel'])

        for logro_data in plan.get('logros', []):
            sp_create_logro(goal_id=goal_id, name=logro_data['name'],
                            description=logro_data['description'], icon=logro_data.get('icon', '🏆'))

        return Response(_build_full_plan(goal, user_id), status=status.HTTP_201_CREATED)


class GoalListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Listar metas del usuario con progreso")
    def get(self, request):
        goals = sp_get_goals_by_user(request.user.id)
        return Response({'goals': goals})


class GoalDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Detalle de una meta: pasos + videos + logros")
    def get(self, request, goal_id: int):
        goal = sp_get_goal_detail(goal_id, request.user.id)
        if not goal:
            return Response({'error': 'Meta no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(_build_full_plan(goal, request.user.id))
