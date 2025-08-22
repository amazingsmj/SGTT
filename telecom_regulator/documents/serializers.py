from rest_framework import serializers
from django.conf import settings
from .models import Document
import os


class DocumentSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Document
        fields = [
            'id', 'owner', 'owner_email', 'titre', 'demande', 'file', 'version',
            'mime_type', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'version', 'created_at', 'updated_at']

    def validate_file(self, file):
        max_size = getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 20 * 1024 * 1024)
        if file.size > max_size:
            raise serializers.ValidationError('Fichier trop volumineux.')
        allowed_ext = {'.pdf', '.jpg', '.jpeg', '.png', '.docx', '.xlsx'}
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_ext:
            raise serializers.ValidationError('Format de fichier non supporté.')
        return file

    def validate(self, attrs):
        titre = attrs.get('titre')
        demande = attrs.get('demande')
        if not titre and not demande:
            raise serializers.ValidationError('Un document doit être associé à un titre ou une demande.')
        if titre and demande:
            raise serializers.ValidationError("Un document ne peut pas être associé aux deux simultanément.")
        return attrs

    def create(self, validated_data):
        titre = validated_data.get('titre')
        demande = validated_data.get('demande')
        qs = Document.objects.all()
        if titre:
            qs = qs.filter(titre=titre)
        if demande:
            qs = qs.filter(demande=demande)
        last = qs.order_by('-version').first()
        validated_data['version'] = (last.version + 1) if last else 1
        return super().create(validated_data)