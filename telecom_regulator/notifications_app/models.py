from django.db import models
from django.conf import settings
import uuid


class Notification(models.Model):
    class Category(models.TextChoices):
        DEMANDE_STATUT = 'demande_statut', 'Changement statut demande'
        TITRE_EXPIRATION = 'titre_expiration', 'Alerte expiration titre'
        SYSTEM = 'system', 'Système'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    category = models.CharField(max_length=50, choices=Category.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Notif {self.category} -> {self.user.email}"
