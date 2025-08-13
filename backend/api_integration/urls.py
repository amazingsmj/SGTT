# api_integration/urls.py
from django.urls import path
from . import views

urlpatterns = [
	# API Keys
	path('api-keys/', views.APIKeyListView.as_view(), name='api_key_list'),
	path('api-keys/<uuid:pk>/', views.APIKeyDetailView.as_view(), name='api_key_detail'),
	path('api-keys/<uuid:pk>/regenerate/', views.regenerate_api_key, name='api_key_regenerate'),

	# API Requests
	path('requests/', views.APIRequestListView.as_view(), name='api_request_list'),
	path('stats/', views.api_statistics, name='api_statistics'),

	# Webhooks
	path('webhooks/', views.WebhookListView.as_view(), name='webhook_list'),
	path('webhooks/<uuid:pk>/', views.WebhookDetailView.as_view(), name='webhook_detail'),
	path('webhooks/<uuid:pk>/test/', views.test_webhook, name='webhook_test'),
	path('deliveries/', views.WebhookDeliveryListView.as_view(), name='webhook_delivery_list'),
	path('deliveries/<uuid:pk>/retry/', views.retry_webhook_delivery, name='webhook_delivery_retry'),

	# External services
	path('services/', views.ExternalServiceListView.as_view(), name='external_service_list'),
	path('services/<uuid:pk>/', views.ExternalServiceDetailView.as_view(), name='external_service_detail'),
	path('services/<uuid:pk>/health/', views.check_service_health, name='external_service_health'),
	path('services/health/', views.check_service_health, name='external_services_health_all'),

	# Documentation & dashboard
	path('docs/', views.api_documentation, name='api_documentation'),
	path('dashboard/', views.integration_dashboard, name='integration_dashboard'),

	# Incoming webhooks
	path('webhooks/incoming/<str:source>/', views.receive_webhook, name='receive_webhook'),
]