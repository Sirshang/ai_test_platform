import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from apps.apitest.models import ApiTestCase
from apps.projects.models import Project, ProjectMember

SAMPLE_SWAGGER = {
    "swagger": "2.0",
    "info": {"title": "Demo API", "version": "1.0.0"},
    "paths": {
        "/users": {
            "get": {
                "summary": "List users",
                "description": "Returns all users",
            },
            "post": {
                "summary": "Create user",
            },
        },
        "/users/{id}": {
            "get": {
                "operationId": "getUserById",
                "description": "Get one user",
            },
        },
    },
}

SAMPLE_SWAGGER_YAML = """
swagger: "2.0"
paths:
  /health:
    get:
      summary: Health check
"""


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
    project = Project.objects.create(name="Swagger Project", owner=user)
    ProjectMember.objects.create(project=project, user=user)
    return project


@pytest.fixture
def other_project(other_user: User) -> Project:
    project = Project.objects.create(name="Other Project", owner=other_user)
    ProjectMember.objects.create(project=project, user=other_user)
    return project


@pytest.mark.django_db
def test_import_swagger_json_creates_draft_cases(
    api_client: APIClient,
    user: User,
    project: Project,
) -> None:
    api_client.force_authenticate(user=user)

    response = api_client.post(
        f"/api/projects/{project.pk}/import-swagger/",
        {"spec": SAMPLE_SWAGGER},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created_count"] == 3

    cases = ApiTestCase.objects.filter(project=project).order_by("id")
    assert cases.count() == 3
    assert all(case.status == ApiTestCase.DRAFT for case in cases)
    assert all(case.script == "" for case in cases)

    titles = {case.title for case in cases}
    assert "List users" in titles
    assert "Create user" in titles
    assert "getUserById" in titles


@pytest.mark.django_db
def test_imported_cases_appear_in_api_case_list(
    api_client: APIClient,
    user: User,
    project: Project,
) -> None:
    api_client.force_authenticate(user=user)
    api_client.post(
        f"/api/projects/{project.pk}/import-swagger/",
        SAMPLE_SWAGGER,
        format="json",
    )

    response = api_client.get(f"/api/api-cases/?project={project.pk}")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    assert {item["method"] for item in response.data} == {"GET", "POST"}


@pytest.mark.django_db
def test_import_swagger_yaml_content(
    api_client: APIClient,
    user: User,
    project: Project,
) -> None:
    api_client.force_authenticate(user=user)

    response = api_client.post(
        f"/api/projects/{project.pk}/import-swagger/",
        {"content": SAMPLE_SWAGGER_YAML, "format": "yaml"},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["created_count"] == 1

    case = ApiTestCase.objects.get(project=project)
    assert case.title == "Health check"
    assert case.method == "GET"
    assert case.path == "/health"


@pytest.mark.django_db
def test_non_member_cannot_import_swagger(
    api_client: APIClient,
    user: User,
    other_project: Project,
) -> None:
    api_client.force_authenticate(user=user)

    response = api_client.post(
        f"/api/projects/{other_project.pk}/import-swagger/",
        {"spec": SAMPLE_SWAGGER},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_import_invalid_swagger_returns_400(
    api_client: APIClient,
    user: User,
    project: Project,
) -> None:
    api_client.force_authenticate(user=user)

    response = api_client.post(
        f"/api/projects/{project.pk}/import-swagger/",
        {"spec": {"info": {"title": "No paths"}}},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ApiTestCase.objects.filter(project=project).count() == 0
