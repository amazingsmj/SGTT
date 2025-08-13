from django.db import models
from django.conf import settings
import uuid


class Demande(models.Model):
    class Status(models.TextChoices):
        SOUMISE = 'soumise', 'Soumise'
        EN_EXAMEN = 'en_examen', 'En examen'
        APPROUVEE = 'approuvee', 'Approuvée'
        REJETEE = 'rejetee', 'Rejetée'

    class TypeTitre(models.TextChoices):
        LICENCE_1 = 'licence_type_1', 'Licence de type 1'
        LICENCE_2 = 'licence_type_2', 'Licence de type 2'
        AGREMENT_VENDEURS = 'agrement_vendeurs', 'Agrément vendeurs'
        AGREMENT_INSTALLATEURS = 'agrement_installateurs', 'Agrément installateurs'
        CONCESSION = 'concessions', 'Concessions'
        RECEPISSE = 'recepisse', 'Récépissé'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    demandeur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='demandes')
    entreprise = models.CharField(max_length=255)
    email_contact = models.EmailField()
    telephone = models.CharField(max_length=50, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    type_titre = models.CharField(max_length=50, choices=TypeTitre.choices)
    description = models.TextField(blank=True, null=True)
    motivations = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SOUMISE)
    numero_dossier = models.CharField(max_length=100, blank=True, null=True)
    date_soumission = models.DateField(auto_now_add=True)
    date_traitement = models.DateField(blank=True, null=True)
    commentaires_admin = models.TextField(blank=True, null=True)
    documents_urls = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Demande {self.id} - {self.get_type_titre_display()}"
