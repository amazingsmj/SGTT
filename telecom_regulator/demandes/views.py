from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Demande
from .serializers import DemandeSerializer
from common.permissions import IsAdminOrStaff


class DemandeViewSet(viewsets.ModelViewSet):
    queryset = Demande.objects.all().order_by('-created_at')
    serializer_class = DemandeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'type_titre', 'demandeur']
    search_fields = ['numero_dossier', 'entreprise', 'email_contact']
    ordering_fields = ['date_soumission', 'date_traitement', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'operateur':
            return qs.filter(demandeur=user)
        return qs

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrStaff()]
        return super().get_permissions()
