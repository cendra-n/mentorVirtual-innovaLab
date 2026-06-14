from django.contrib.auth.models import User
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status


class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined').values(
            'id', 'username', 'email', 'is_active', 'is_staff', 'date_joined'
        )
        return Response({'users': list(users)})


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            u = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)
        return Response({
            'id': u.id, 'username': u.username, 'email': u.email,
            'is_active': u.is_active, 'is_staff': u.is_staff,
            'date_joined': u.date_joined,
        })

    def patch(self, request, user_id):
        try:
            u = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)

        if 'is_active' in request.data:
            u.is_active = request.data['is_active']
        if 'is_staff' in request.data:
            u.is_staff = request.data['is_staff']
        u.save()
        return Response({'message': 'Usuario actualizado.'})


class AdminSetPasswordView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            u = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)

        password = request.data.get('password', '')
        if len(password) < 8:
            return Response(
                {'error': 'La contraseña debe tener al menos 8 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        u.set_password(password)   # hashea correctamente
        u.save()
        return Response({'message': f'Contraseña de {u.username} actualizada correctamente.'})


class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        with connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM auth_user")
            total_users = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM goals")
            total_goals = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM user_progress")
            total_steps_completed = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM video_views")
            total_video_views = cur.fetchone()[0]

        return Response({
            'total_users':           total_users,
            'total_goals':           total_goals,
            'total_steps_completed': total_steps_completed,
            'total_video_views':     total_video_views,
        })
