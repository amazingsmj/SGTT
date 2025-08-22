from django.shortcuts import render
from rest_framework import viewsets, permissions, filters, decorators, response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Titre
from .serializers import TitreSerializer
from common.permissions import IsAdminOrStaff
from .services import calculate_redevance


class TitreViewSet(viewsets.ModelViewSet):
    queryset = Titre.objects.all().order_by('-created_at')
    serializer_class = TitreSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'status', 'proprietaire']
    search_fields = ['numero_titre', 'entreprise_nom', 'description']
    ordering_fields = ['date_emission', 'date_expiration', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrStaff()]
        return super().get_permissions()

    @decorators.action(detail=True, methods=['get'])
    def redevance(self, request, pk=None):
        titre = self.get_object()
        amount = calculate_redevance(titre)
        return response.Response({'redevance': amount})
