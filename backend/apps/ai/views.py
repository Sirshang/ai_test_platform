from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.serializers import GenerateApiScriptSerializer
from apps.ai.services.api_script import generate_api_script
from apps.ai.services.llm import LLMCallError
from apps.ai.services.prompts import PromptTemplateError
from apps.apitest.models import ApiTestCase


class GenerateApiScriptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = GenerateApiScriptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        interfaces = serializer.validated_data["interfaces"]
        case_id = serializer.validated_data.get("case_id")

        try:
            script = generate_api_script(interfaces)
        except PromptTemplateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except LLMCallError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        response_data: dict[str, object] = {"script": script}

        if case_id is not None:
            test_case = get_object_or_404(
                ApiTestCase.objects.filter(project__members__user=request.user),
                pk=case_id,
            )
            test_case.script = script
            test_case.save(update_fields=["script", "updated_at"])
            response_data["case_id"] = test_case.pk

        return Response(response_data, status=status.HTTP_200_OK)
