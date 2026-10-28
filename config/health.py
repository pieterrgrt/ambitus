from django.db import connection
from django.http import HttpResponse


class HealthCheckMiddleware:
    """Answers /health before the host check and HTTPS redirect, so the
    deploy script and Docker can probe the app on 127.0.0.1."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/health":
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
            except Exception:
                return HttpResponse("database unavailable", status=503, content_type="text/plain")
            return HttpResponse("ok", content_type="text/plain")
        return self.get_response(request)
