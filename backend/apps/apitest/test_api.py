import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from apps.apitest.models import ApiTestCase
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


@pytest.fixture
def project(user: User) -> Project:
    project = Project.objects.create(name="API Project", owner=user)
    ProjectMember.objects.create(project=project, user=user)
    return project


@pytest.fixture
def other_project(other_user: User) -> Project:
    project = Project.objects.create(name="Other Project", owner=other_user)
    ProjectMember.objects.create(project=project, user=other_user)
    return project


@pytest.mark.django_db
def test_create_api_case(api_client: APIClient, user: User, project: Project) -> None:
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/api-cases/",
        {
            "project": project.pk,
            "title": "获取用户列表",
            "method": "GET",
            "path": "/api/users",
            "headers": {"Accept": "application/json"},
            "query_params": {"page": "1"},
            "script": "def test_users():\n    pass\n",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == "获取用户列表"
    assert response.data["status"] == ApiTestCase.DRAFT
    assert ApiTestCase.objects.filter(project=project).count() == 1


@pytest.mark.django_db
def test_list_api_cases_filtered_by_project(
    api_client: APIClient,
    user: User,
    project: Project,
    other_project: Project,
) -> None:
    ApiTestCase.objects.create(
        project=project,
        title="Mine",
        method="GET",
        path="/api/mine",
    )
    ApiTestCase.objects.create(
        project=other_project,
        title="Other",
        method="GET",
        path="/api/other",
    )

    api_client.force_authenticate(user=user)
    response = api_client.get(f"/api/api-cases/?project={project.pk}")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Mine"


@pytest.mark.django_db
def test_update_api_case(api_client: APIClient, user: User, project: Project) -> None:
    test_case = ApiTestCase.objects.create(
        project=project,
        title="Old Title",
        method="GET",
        path="/api/old",
        status=ApiTestCase.DRAFT,
    )

    api_client.force_authenticate(user=user)
    response = api_client.patch(
        f"/api/api-cases/{test_case.pk}/",
        {"title": "New Title", "status": ApiTestCase.READY},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    test_case.refresh_from_db()
    assert test_case.title == "New Title"
    assert test_case.status == ApiTestCase.READY


@pytest.mark.django_db
def test_delete_api_case(api_client: APIClient, user: User, project: Project) -> None:
    test_case = ApiTestCase.objects.create(
        project=project,
        title="To Delete",
        method="GET",
        path="/api/delete",
    )

    api_client.force_authenticate(user=user)
    response = api_client.delete(f"/api/api-cases/{test_case.pk}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not ApiTestCase.objects.filter(pk=test_case.pk).exists()


@pytest.mark.django_db
def test_non_member_cannot_create_case_for_project(
    api_client: APIClient,
    user: User,
    other_project: Project,
) -> None:
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/api-cases/",
        {
            "project": other_project.pk,
            "title": "Forbidden",
            "method": "GET",
            "path": "/api/forbidden",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "project" in response.data


@pytest.mark.django_db
def test_non_member_cannot_retrieve_case(
    api_client: APIClient,
    user: User,
    other_project: Project,
) -> None:
    test_case = ApiTestCase.objects.create(
        project=other_project,
        title="Private",
        method="GET",
        path="/api/private",
    )

    api_client.force_authenticate(user=user)
    response = api_client.get(f"/api/api-cases/{test_case.pk}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_unauthenticated_request_is_denied(api_client: APIClient) -> None:
    response = api_client.get("/api/api-cases/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
