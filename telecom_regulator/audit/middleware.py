from .models import AuditLog
from django.utils.deprecation import MiddlewareMixin


class AuditMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and request.path.startswith('/api/'):
            user = getattr(request, 'user', None)
            AuditLog.objects.create(
                user=user if user and user.is_authenticated else None,
                action=f"{request.method} {request.path}",
                model=view_func.__module__,
                object_id='-',
                ip_address=request.META.get('REMOTE_ADDR'),
                changes={},
            )
        return None