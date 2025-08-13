from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


def upload_to(instance, filename):
    return f"documents/{instance.owner_id}/{timezone.now().strftime('%Y/%m/%d')}/{filename}"


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    titre = models.ForeignKey('titles.Titre', on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    demande = models.ForeignKey('demandes.Demande', on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    file = models.FileField(upload_to=upload_to)
    version = models.PositiveIntegerField(default=1)
    mime_type = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('titre', 'demande', 'version', 'file')

    def __str__(self) -> str:
        target = self.titre or self.demande
        return f"Document v{self.version} -> {target}"
