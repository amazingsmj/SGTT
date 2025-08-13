from rest_framework import views, permissions, response
from django.db.models import Count
from titles.models import Titre
from demandes.models import Demande
from django.contrib.auth import get_user_model


class StatsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        User = get_user_model()
        data = {
            'users_count': User.objects.count(),
            'titles_count': Titre.objects.count(),
            'demandes_count': Demande.objects.count(),
            'titles_by_status': Titre.objects.values('status').annotate(c=Count('id')).order_by(),
            'demandes_by_status': Demande.objects.values('status').annotate(c=Count('id')).order_by(),
        }
        return response.Response(data)
