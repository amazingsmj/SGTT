from rest_framework import serializers
from .models import Demande
import uuid as uuid_lib


class DemandeSerializer(serializers.ModelSerializer):
    demandeur_email = serializers.ReadOnlyField(source='demandeur.email')

    class Meta:
        model = Demande
        fields = [
            'id', 'demandeur', 'demandeur_email', 'entreprise', 'email_contact', 'telephone',
            'adresse', 'type_titre', 'description', 'motivations', 'status', 'numero_dossier',
            'date_soumission', 'date_traitement', 'commentaires_admin', 'documents_urls',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'numero_dossier', 'date_soumission', 'created_at', 'updated_at']

    def create(self, validated_data):
        if not validated_data.get('numero_dossier'):
            validated_data['numero_dossier'] = f"DOS-{uuid_lib.uuid4().hex[:10].upper()}"
        return super().create(validated_data)