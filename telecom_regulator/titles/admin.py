from django.contrib import admin
from .models import Titre


@admin.register(Titre)
class TitreAdmin(admin.ModelAdmin):
    list_display = ('numero_titre', 'type', 'proprietaire', 'status', 'date_emission', 'date_expiration')
    list_filter = ('type', 'status')
    search_fields = ('numero_titre', 'entreprise_nom', 'proprietaire__email')
