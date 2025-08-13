# api_integration/models.py
from django.db import models
import uuid


class TimestampedModel(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class APIKey(TimestampedModel):
	STATUS_CHOICES = [
		('active', 'Active'),
		('revoked', 'Revoked'),
	]
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=255)
	key = models.CharField(max_length=64, unique=True)
	secret = models.CharField(max_length=128)
	is_active = models.BooleanField(default=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

	@staticmethod
	def generate_key():
		import secrets
		return secrets.token_hex(16)

	@staticmethod
	def generate_secret():
		import secrets
		return secrets.token_urlsafe(48)

	def __str__(self):
		return f"{self.name} ({self.status})"


class APIRequest(TimestampedModel):
	METHOD_CHOICES = [
		('GET', 'GET'),
		('POST', 'POST'),
		('PUT', 'PUT'),
		('PATCH', 'PATCH'),
		('DELETE', 'DELETE'),
	]
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
	path = models.CharField(max_length=512)
	method = models.CharField(max_length=10, choices=METHOD_CHOICES)
	status_code = models.IntegerField()
	timestamp = models.DateTimeField(auto_now_add=True)
	latency_ms = models.IntegerField(default=0)


class Webhook(TimestampedModel):
	STATUS_CHOICES = [
		('active', 'Active'),
		('disabled', 'Disabled'),
	]
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=255)
	url = models.URLField()
	secret = models.CharField(max_length=128, blank=True, null=True)
	is_active = models.BooleanField(default=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
	retry_policy = models.JSONField(default=dict, blank=True)


class WebhookDelivery(TimestampedModel):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('success', 'Success'),
		('failed', 'Failed'),
	]
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
	event = models.CharField(max_length=255)
	payload = models.JSONField(default=dict)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	attempts = models.IntegerField(default=0)
	next_retry = models.DateTimeField(blank=True, null=True)
	response_status = models.IntegerField(blank=True, null=True)
	response_body = models.TextField(blank=True, null=True)


class ExternalService(TimestampedModel):
	STATUS_CHOICES = [
		('up', 'Up'),
		('down', 'Down'),
		('error', 'Error'),
		('maintenance', 'Maintenance'),
	]
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=255, unique=True)
	base_url = models.URLField(blank=True, null=True)
	auth_type = models.CharField(max_length=50, default='none')
	credentials = models.JSONField(default=dict, blank=True)
	is_active = models.BooleanField(default=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='up')
	last_checked_at = models.DateTimeField(blank=True, null=True)
	last_error = models.TextField(blank=True, null=True)


class ServiceHealthCheck(TimestampedModel):
	STATUS_CHOICES = [
		('up', 'Up'),
		('down', 'Down'),
		('degraded', 'Degraded'),
	]
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	service = models.ForeignKey(ExternalService, on_delete=models.CASCADE, related_name='health_checks')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES)
	checked_at = models.DateTimeField(auto_now_add=True)
	latency_ms = models.IntegerField(default=0)
	metadata = models.JSONField(default=dict, blank=True)