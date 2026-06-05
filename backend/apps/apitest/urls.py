from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.apitest.views import ApiTestCaseViewSet, ImportSwaggerView

router = DefaultRouter()
router.register("api-cases", ApiTestCaseViewSet, basename="api-case")

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/projects/<int:project_id>/import-swagger/",
        ImportSwaggerView.as_view(),
        name="import-swagger",
    ),
]
