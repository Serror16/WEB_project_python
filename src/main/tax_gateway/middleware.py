import time
import json
from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog

class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware для перехвата запросов и ответов API,
    расчета времени выполнения и сохранения в БД.
    """
    def process_request(self, request):
        # отсчет времени обработки запроса
        request.start_time = time.time()

        # безопасное чтение тела запроса
        request.audit_request_body = None
        if request.body:
            try:
                request.audit_request_body = json.loads(request.body.decode('utf-8'))
            except Exception:
                # сохранение тела запроса в виде текста, если пришел не json
                request.audit_request_body = {"raw_data": request.body.decode('utf-8', errors='replace')}

    def process_response(self, request, response):
        # если время не было зафиксировано
        if not hasattr(request, 'start_time'):
            return response

        # подсчет времени выполнения
        processing_time_ms = (time.time() - request.start_time) * 1000

        # безопасное чтение тела ответа
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

        response_body = None
        if hasattr(response, 'content'):
            try:
                response_body = json.loads(response.content.decode('utf-8'))
            except Exception:
                response_body = {"raw_data": response.content.decode('utf-8', errors='replace')}

        # логируются только api и эндпоинты
        if request.path.startswith('/api/'):
            AuditLog.objects.create(
                path=request.path,
                method=request.method,
                user=user,
                status_code=response.status_code,
                processing_time_ms=processing_time_ms,
                request_payload=getattr(request, 'audit_request_body', None),
                response_payload=response_body,
            )

        return response