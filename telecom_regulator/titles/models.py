from django.db import models
from django.conf import settings
import uuid


class Titre(models.Model):
    class Type(models.TextChoices):
        LICENCE_1 = 'licence_type_1', 'Licence de type 1'
        LICENCE_2 = 'licence_type_2', 'Licence de type 2'
        AGREMENT_VENDEURS = 'agrement_vendeurs', 'Agrément vendeurs'
        AGREMENT_INSTALLATEURS = 'agrement_installateurs', 'Agrément installateurs'
        CONCESSION = 'concessions', 'Concessions'
        RECEPISSE = 'recepisse', 'Récépissé'

    class Status(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        EN_COURS = 'en_cours', 'En cours'
        APPROUVE = 'approuve', 'Approuvé'
        REJETE = 'rejete', 'Rejeté'
        EXPIRE = 'expire', 'Expiré'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_titre = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=50, choices=Type.choices)
    proprietaire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='titres')
    entreprise_nom = models.CharField(max_length=255)
    date_emission = models.DateField()
    date_expiration = models.DateField()
    duree_ans = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EN_ATTENTE)
    description = models.TextField(blank=True, null=True)
    conditions_specifiques = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.numero_titre} - {self.get_type_display()}"
