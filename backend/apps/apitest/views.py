from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.apitest.models import ApiTestCase
from apps.apitest.permissions import IsApiCaseProjectMember
from apps.apitest.serializers import ApiTestCaseSerializer, ImportSwaggerSerializer
from apps.apitest.services.swagger_import import (
    SwaggerParseError,
    import_swagger_cases,
    load_swagger_spec,
)
from apps.projects.models import Project


class ApiTestCaseViewSet(viewsets.ModelViewSet):
    serializer_class = ApiTestCaseSerializer
    permission_classes = [IsApiCaseProjectMember]

    def get_queryset(self) -> QuerySet[ApiTestCase]:
        queryset = ApiTestCase.objects.filter(
            project__members__user=self.request.user,
        ).distinct()

        project_id = self.request.query_params.get("project")
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class ImportSwaggerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id: int) -> Response:
        project = get_object_or_404(
            Project.objects.filter(members__user=request.user),
            pk=project_id,
        )

        input_serializer = ImportSwaggerSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            spec = load_swagger_spec(request.data)
            cases = import_swagger_cases(project, spec)
        except SwaggerParseError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        case_serializer = ApiTestCaseSerializer(
            cases,
            many=True,
            context={"request": request},
        )
        return Response(
            {
                "created_count": len(cases),
                "cases": case_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
