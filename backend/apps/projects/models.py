from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Project(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_projects",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class ProjectMember(BaseModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )

    class Meta:
        unique_together = ("project", "user")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user} @ {self.project}"
