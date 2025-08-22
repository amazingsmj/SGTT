from django.shortcuts import render
from rest_framework import viewsets, permissions, decorators, response
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Notification.objects.all().order_by('-created_at')
        return Notification.objects.filter(user=user).order_by('-created_at')

    @decorators.action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return response.Response({'status': 'read'})
