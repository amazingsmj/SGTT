# api_integration/serializers.py
from rest_framework import serializers
from .models import APIKey, APIRequest, Webhook, WebhookDelivery, ExternalService, ServiceHealthCheck


class APIKeySerializer(serializers.ModelSerializer):
	class Meta:
		model = APIKey
		fields = ['id', 'name', 'key', 'secret', 'is_active', 'status', 'created_at', 'updated_at']
		read_only_fields = ['key', 'secret', 'created_at', 'updated_at']


class APIRequestSerializer(serializers.ModelSerializer):
	class Meta:
		model = APIRequest
		fields = ['id', 'api_key', 'path', 'method', 'status_code', 'timestamp', 'latency_ms']


class WebhookSerializer(serializers.ModelSerializer):
	class Meta:
		model = Webhook
		fields = ['id', 'name', 'url', 'secret', 'is_active', 'status', 'retry_policy', 'created_at', 'updated_at']


class WebhookDeliverySerializer(serializers.ModelSerializer):
	webhook_name = serializers.CharField(source='webhook.name', read_only=True)

	class Meta:
		model = WebhookDelivery
		fields = ['id', 'webhook', 'webhook_name', 'event', 'payload', 'status', 'attempts', 'next_retry', 'response_status', 'response_body', 'created_at']


class ExternalServiceSerializer(serializers.ModelSerializer):
	class Meta:
		model = ExternalService
		fields = ['id', 'name', 'base_url', 'auth_type', 'credentials', 'is_active', 'status', 'last_checked_at', 'last_error', 'created_at', 'updated_at']


class ServiceHealthCheckSerializer(serializers.ModelSerializer):
	service_name = serializers.CharField(source='service.name', read_only=True)

	class Meta:
		model = ServiceHealthCheck
		fields = ['id', 'service', 'service_name', 'status', 'checked_at', 'latency_ms', 'metadata']


class APIDocumentationSerializer(serializers.Serializer):
	title = serializers.CharField()
	version = serializers.CharField()
	description = serializers.CharField()
	base_url = serializers.CharField()
	authentication = serializers.DictField()
	endpoints = serializers.ListField(child=serializers.DictField())


class APIStatisticsSerializer(serializers.Serializer):
	total_requests = serializers.IntegerField()
	success_rate = serializers.FloatField()
	requests_per_method = serializers.DictField()
	requests_per_status = serializers.DictField()
	recent_errors = serializers.ListField(child=serializers.DictField())