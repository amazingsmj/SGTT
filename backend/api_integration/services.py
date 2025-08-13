# api_integration/services.py
import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional

import requests
from django.db.models import Count
from django.urls import get_resolver
from django.utils import timezone

from .models import (
	APIKey,
	APIRequest,
	ExternalService,
	ServiceHealthCheck,
	Webhook,
	WebhookDelivery,
)


class APIKeyService:
	"""Services utilitaires pour la gestion des clés API."""

	@staticmethod
	def create_api_key(name: str, is_active: bool = True) -> APIKey:
		new_key_value = APIKey.generate_key()
		new_secret_value = APIKey.generate_secret()
		api_key = APIKey.objects.create(
			name=name,
			key=new_key_value,
			secret=new_secret_value,
			is_active=is_active,
			status='active' if is_active else 'revoked',
		)
		return api_key

	@staticmethod
	def regenerate(api_key: APIKey) -> APIKey:
		api_key.key = APIKey.generate_key()
		api_key.secret = APIKey.generate_secret()
		api_key.save(update_fields=['key', 'secret', 'updated_at'])
		return api_key

	@staticmethod
	def revoke(api_key: APIKey) -> APIKey:
		api_key.is_active = False
		api_key.status = 'revoked'
		api_key.save(update_fields=['is_active', 'status', 'updated_at'])
		return api_key


class WebhookService:
	"""Gestion des envois de webhooks sortants et des livraisons."""

	DEFAULT_RETRY_POLICY = {
		'max_attempts': 5,
		'initial_delay_seconds': 30,
		'backoff_factor': 2,
	}

	@staticmethod
	def _compute_signature(secret: str, payload: Dict[str, Any]) -> str:
		serialized = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
		digest = hmac.new(secret.encode('utf-8'), serialized, hashlib.sha256).hexdigest()
		return f"sha256={digest}"

	@staticmethod
	def _determine_next_retry(attempts: int, retry_policy: Dict[str, Any]) -> Optional[timezone.datetime]:
		max_attempts = int(retry_policy.get('max_attempts', WebhookService.DEFAULT_RETRY_POLICY['max_attempts']))
		if attempts >= max_attempts:
			return None
		initial_delay = int(retry_policy.get('initial_delay_seconds', WebhookService.DEFAULT_RETRY_POLICY['initial_delay_seconds']))
		backoff = int(retry_policy.get('backoff_factor', WebhookService.DEFAULT_RETRY_POLICY['backoff_factor']))
		delay_seconds = initial_delay * (backoff ** max(0, attempts - 1)) if attempts > 0 else initial_delay
		return timezone.now() + timezone.timedelta(seconds=delay_seconds)

	@staticmethod
	def send_webhook(event: str, payload: Dict[str, Any], webhook_id: Any) -> WebhookDelivery:
		webhook: Webhook = Webhook.objects.get(pk=webhook_id)
		retry_policy = webhook.retry_policy or WebhookService.DEFAULT_RETRY_POLICY

		# Enregistrer la livraison en attente
		delivery = WebhookDelivery.objects.create(
			webhook=webhook,
			event=event,
			payload=payload,
			status='pending',
			attempts=0,
		)

		if not webhook.is_active or webhook.status != 'active':
			delivery.status = 'failed'
			delivery.response_body = 'Webhook inactive'
			delivery.response_status = 0
			delivery.next_retry = None
			delivery.save(update_fields=['status', 'response_body', 'response_status', 'next_retry', 'updated_at'])
			return delivery

		headers: Dict[str, str] = {
			'Content-Type': 'application/json',
			'X-Webhook-Event': event,
			'X-Webhook-Id': str(webhook.id),
		}
		if webhook.secret:
			headers['X-Webhook-Signature'] = WebhookService._compute_signature(webhook.secret, payload)

		start_time = time.perf_counter()
		response_status: int
		response_body_text: str

		try:
			response = requests.post(webhook.url, headers=headers, data=json.dumps(payload), timeout=10)
			response_status = response.status_code
			# Truncate large bodies to avoid DB bloat
			response_body_text = response.text[:2000] if response.text else ''
			status_success = 200 <= response_status < 300
			new_status = 'success' if status_success else 'failed'
		except Exception as exc:
			response_status = 0
			response_body_text = f"Exception: {exc}"
			new_status = 'failed'

		latency_ms = int((time.perf_counter() - start_time) * 1000)

		# Mettre à jour la livraison
		delivery.attempts = 1
		delivery.status = new_status
		delivery.response_status = response_status
		delivery.response_body = response_body_text
		delivery.next_retry = None if new_status == 'success' else WebhookService._determine_next_retry(delivery.attempts, retry_policy)
		delivery.save(update_fields=['attempts', 'status', 'response_status', 'response_body', 'next_retry', 'updated_at'])

		return delivery


class ExternalServiceService:
	"""Vérification de santé des services externes."""

	@staticmethod
	def _health_check_url(base_url: Optional[str]) -> Optional[str]:
		if not base_url:
			return None
		# Essaye d'appeler /health si présent, sinon la racine
		return base_url.rstrip('/') + '/health'

	@staticmethod
	def check_service_health(service_id: Optional[Any] = None) -> None:
		if service_id is not None:
			services_to_check = ExternalService.objects.filter(pk=service_id, is_active=True)
		else:
			services_to_check = ExternalService.objects.filter(is_active=True)

		for service in services_to_check:
			url = ExternalServiceService._health_check_url(service.base_url) or service.base_url
			if not url:
				# Enregistre un check down si pas d'URL
				ServiceHealthCheck.objects.create(
					service=service,
					status='down',
					latency_ms=0,
					metadata={'reason': 'No base_url configured'},
				)
				service.status = 'error'
				service.last_checked_at = timezone.now()
				service.last_error = 'No base_url configured'
				service.save(update_fields=['status', 'last_checked_at', 'last_error', 'updated_at'])
				continue

			start_time = time.perf_counter()
			result_status = 'down'
			latency_ms = 0
			metadata: Dict[str, Any] = {}
			try:
				response = requests.get(url, timeout=5)
				latency_ms = int((time.perf_counter() - start_time) * 1000)
				metadata = {'url': url, 'status_code': response.status_code}
				if 200 <= response.status_code < 300:
					result_status = 'up'
				elif 500 <= response.status_code < 600:
					result_status = 'down'
				else:
					result_status = 'degraded'
			except Exception as exc:
				latency_ms = int((time.perf_counter() - start_time) * 1000)
				metadata = {'url': url, 'exception': str(exc)}
				result_status = 'down'

			# Persister le check
			ServiceHealthCheck.objects.create(
				service=service,
				status=result_status,
				latency_ms=latency_ms,
				metadata=metadata,
			)

			# Mettre à jour le service
			service.last_checked_at = timezone.now()
			if result_status == 'up':
				service.status = 'up'
				service.last_error = None
			elif result_status == 'degraded':
				service.status = 'maintenance'
				service.last_error = json.dumps(metadata)[:1000]
			else:
				service.status = 'error'
				service.last_error = json.dumps(metadata)[:1000]
			service.save(update_fields=['status', 'last_checked_at', 'last_error', 'updated_at'])


class APIDocumentationService:
	"""Prépare des informations de documentation de l'API."""

	@staticmethod
	def get_authentication_info() -> Dict[str, Any]:
		return {
			'type': 'JWT Bearer',
			'header': 'Authorization: Bearer <token>',
			'token_endpoints': {
				'obtain': '/api/users/token/',
				'refresh': '/api/users/token/refresh/',
			},
		}

	@staticmethod
	def get_api_endpoints() -> List[Dict[str, Any]]:
		endpoints: List[Dict[str, Any]] = []
		resolver = get_resolver()

		def _walk_patterns(patterns, prefix: str = '') -> None:
			for entry in patterns:
				pattern_str = getattr(entry, 'pattern', None)
				if hasattr(entry, 'url_patterns'):
					_wPrefix = prefix + str(pattern_str)
					_walk_patterns(entry.url_patterns, prefix=_wPrefix)
				else:
					try:
						route = prefix + str(pattern_str)
						name = getattr(entry, 'name', None)
						callback = getattr(entry, 'callback', None)
						view_name = getattr(callback, '__name__', None) if callback else None
						endpoints.append({
							'route': '/' + route.lstrip('^').rstrip('$'),
							'name': name,
							'view': view_name,
						})
					except Exception:
						# Ignore malformed entries
						pass

		try:
			_walk_patterns(resolver.url_patterns)
		except Exception:
			pass

		# Tri et déduplication basique
		unique = []
		seen = set()
		for ep in endpoints:
			key = (ep.get('route'), ep.get('name'))
			if key in seen:
				continue
			seen.add(key)
			unique.append(ep)
		return unique


class APIStatisticsService:
	"""Calcule des statistiques d'usage de l'API."""

	@staticmethod
	def get_api_statistics(days: int = 30) -> Dict[str, Any]:
		start_date = timezone.now() - timezone.timedelta(days=days)
		queryset = APIRequest.objects.filter(timestamp__gte=start_date)

		total_requests = queryset.count()
		successful_requests = queryset.filter(status_code__gte=200, status_code__lt=300).count()
		success_rate = float(successful_requests) / float(total_requests) if total_requests > 0 else 0.0

		# Répartition par méthode
		method_counts = queryset.values('method').annotate(count=Count('id'))
		requests_per_method: Dict[str, int] = {row['method']: row['count'] for row in method_counts}

		# Répartition par classe de statut (2xx, 4xx, 5xx)
		status_buckets = {
			'2xx': queryset.filter(status_code__gte=200, status_code__lt=300).count(),
			'3xx': queryset.filter(status_code__gte=300, status_code__lt=400).count(),
			'4xx': queryset.filter(status_code__gte=400, status_code__lt=500).count(),
			'5xx': queryset.filter(status_code__gte=500, status_code__lt=600).count(),
		}

		# Erreurs récentes
		recent_errors_qs = queryset.filter(status_code__gte=400).order_by('-timestamp')[:10]
		recent_errors: List[Dict[str, Any]] = list(
			recent_errors_qs.values('path', 'method', 'status_code', 'timestamp')
		)

		return {
			'total_requests': total_requests,
			'success_rate': round(success_rate, 4),
			'requests_per_method': requests_per_method,
			'requests_per_status': status_buckets,
			'recent_errors': recent_errors,
		}