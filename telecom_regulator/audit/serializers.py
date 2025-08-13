from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_email', 'action', 'model', 'object_id', 'changes', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']