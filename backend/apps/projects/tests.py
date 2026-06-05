import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from apps.projects.models import Project, ProjectMember


@pytest.mark.django_db
def test_create_project_and_add_member() -> None:
    owner = User.objects.create_user(username="owner", password="pass")
    member = User.objects.create_user(username="member", password="pass")

    project = Project.objects.create(
        name="AITS Demo",
        description="MVP 测试项目",
        owner=owner,
    )
    ProjectMember.objects.create(project=project, user=member)

    assert Project.objects.count() == 1
    assert project.members.count() == 1
    assert project.members.first().user == member
    assert project.owner == owner
    assert project.created_at is not None
    assert project.updated_at is not None


@pytest.mark.django_db
def test_project_member_unique_together() -> None:
    owner = User.objects.create_user(username="owner", password="pass")
    project = Project.objects.create(name="Unique Test", owner=owner)

    ProjectMember.objects.create(project=project, user=owner)

    with pytest.raises(IntegrityError):
        ProjectMember.objects.create(project=project, user=owner)
