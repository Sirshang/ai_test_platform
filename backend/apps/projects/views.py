from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.request import Request

from apps.projects.models import Project, ProjectMember
from apps.projects.permissions import IsProjectMember
from apps.projects.serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectMember]

    def get_queryset(self) -> QuerySet[Project]:
        return Project.objects.filter(members__user=self.request.user).distinct()

    def perform_create(self, serializer: ProjectSerializer) -> None:
        project = serializer.save(owner=self.request.user)
        ProjectMember.objects.create(project=project, user=self.request.user)
