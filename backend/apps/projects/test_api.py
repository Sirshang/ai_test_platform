import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project, ProjectMember


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(username="alice", password="pass1234")


@pytest.fixture
def other_user(db) -> User:
    return User.objects.create_user(username="bob", password="pass1234")


@pytest.mark.django_db
def test_create_project_sets_owner_and_member(api_client: APIClient, user: User) -> None:
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/projects/",
        {"name": "New Project", "description": "desc"},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "New Project"
    assert response.data["owner"] == "alice"

    project = Project.objects.get(pk=response.data["id"])
    assert project.owner == user
    assert project.members.filter(user=user).exists()


@pytest.mark.django_db
def test_list_projects_only_shows_member_projects(
    api_client: APIClient,
    user: User,
    other_user: User,
) -> None:
    owned = Project.objects.create(name="Mine", owner=user)
    ProjectMember.objects.create(project=owned, user=user)

    other_project = Project.objects.create(name="Other", owner=other_user)
    ProjectMember.objects.create(project=other_project, user=other_user)

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/projects/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Mine"


@pytest.mark.django_db
def test_non_member_cannot_retrieve_project(
    api_client: APIClient,
    user: User,
    other_user: User,
) -> None:
    project = Project.objects.create(name="Private", owner=other_user)
    ProjectMember.objects.create(project=project, user=other_user)

    api_client.force_authenticate(user=user)
    response = api_client.get(f"/api/projects/{project.pk}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_unauthenticated_request_is_denied(api_client: APIClient) -> None:
    response = api_client.get("/api/projects/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_project_as_member(api_client: APIClient, user: User) -> None:
    project = Project.objects.create(name="Old Name", owner=user)
    ProjectMember.objects.create(project=project, user=user)

    api_client.force_authenticate(user=user)
    response = api_client.patch(
        f"/api/projects/{project.pk}/",
        {"name": "New Name"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    project.refresh_from_db()
    assert project.name == "New Name"


@pytest.mark.django_db
def test_delete_project_as_member(api_client: APIClient, user: User) -> None:
    project = Project.objects.create(name="To Delete", owner=user)
    ProjectMember.objects.create(project=project, user=user)

    api_client.force_authenticate(user=user)
    response = api_client.delete(f"/api/projects/{project.pk}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Project.objects.filter(pk=project.pk).exists()
