from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'titre', 'demande', 'version', 'created_at')
    list_filter = ('version',)
    search_fields = ('owner__email', 'titre__numero_titre', 'demande__numero_dossier')
