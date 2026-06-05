"""URL configuration for AITS MVP."""

from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(["GET"])
def api_test(_request: Request) -> Response:
    """Health check endpoint for frontend proxy verification (T003)."""
    return Response(
        {
            "status": "ok",
            "message": "AITS API mock response",
            "service": "django",
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/test/", api_test, name="api-test"),
    path("", include("apps.projects.urls")),
    path("", include("apps.apitest.urls")),
    path("", include("apps.ai.urls")),
]