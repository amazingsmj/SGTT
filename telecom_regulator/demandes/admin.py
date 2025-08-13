from django.contrib import admin
from .models import Demande


@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):
    list_display = ('numero_dossier', 'type_titre', 'demandeur', 'status', 'date_soumission', 'date_traitement')
    list_filter = ('type_titre', 'status')
    search_fields = ('numero_dossier', 'demandeur__email', 'entreprise')
