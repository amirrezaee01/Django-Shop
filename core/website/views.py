from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views.generic import TemplateView

# Create your views here.


class IndexView(TemplateView):
    template_name = "website/index.html"


class AboutView(TemplateView):
    template_name = "website/about.html"


class ContactViews(TemplateView):
    template_name = "website/contact.html"


def health_check(request):
    """Return a minimal readiness response without exposing configuration."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
