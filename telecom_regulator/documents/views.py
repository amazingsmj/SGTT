from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document
from .serializers import DocumentSerializer


class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['admin', 'personnel'])


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-created_at')
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['titre', 'demande', 'owner']
    search_fields = ['description']
    ordering_fields = ['created_at', 'version']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'operateur':
            return qs.filter(owner=user)
        return qs

    def get_permissions(self):
        if self.action in ['destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrStaff()]
        return super().get_permissions()
