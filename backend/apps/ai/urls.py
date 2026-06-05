from django.urls import path

from apps.ai.views import GenerateApiScriptView

urlpatterns = [
    path(
        "api/ai/generate-api-script/",
        GenerateApiScriptView.as_view(),
        name="generate-api-script",
    ),
]
