from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'model', 'object_id', 'ip_address')
    list_filter = ('action', 'model')
    search_fields = ('user__email', 'model', 'object_id', 'ip_address')
