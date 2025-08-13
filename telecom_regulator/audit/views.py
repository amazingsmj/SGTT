from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import AuditLog
from .serializers import AuditLogSerializer
from common.permissions import IsAdmin


# Create your views here.


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-created_at')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
