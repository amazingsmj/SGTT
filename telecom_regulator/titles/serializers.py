from rest_framework import serializers
from .models import Titre


class TitreSerializer(serializers.ModelSerializer):
    proprietaire_email = serializers.ReadOnlyField(source='proprietaire.email')

    class Meta:
        model = Titre
        fields = [
            'id', 'numero_titre', 'type', 'proprietaire', 'proprietaire_email', 'entreprise_nom',
            'date_emission', 'date_expiration', 'duree_ans', 'status', 'description',
            'conditions_specifiques', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']