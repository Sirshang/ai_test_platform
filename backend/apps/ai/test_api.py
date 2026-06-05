from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from apps.ai.services.llm import LLMCallError
from apps.apitest.models import ApiTestCase
from apps.projects.models import Project, ProjectMember

SAMPLE_INTERFACES = [
    {
        "title": "获取用户列表",
        "method": "GET",
        "path": "/api/users",
        "description": "返回用户列表",
    }
]

MOCK_SCRIPT = (
    'def test_get_users_returns_200(api_client):\n'
    '    response = api_client.get("/api/users")\n'
    "    assert response.status_code == 200\n"
)


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(username="alice", password="pass1234")


@pytest.fixture
def project(user: User) -> Project:
    project = Project.objects.create(name="AI Project", owner=user)
    ProjectMember.objects.create(project=project, user=user)
    return project


@pytest.mark.django_db
@patch("apps.ai.views.generate_api_script", return_value=MOCK_SCRIPT)
def test_generate_api_script_returns_script(
    mock_generate: object,
    api_client: APIClient,
    user: User,
) -> None:
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/ai/generate-api-script/",
        {"interfaces": SAMPLE_INTERFACES},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["script"] == MOCK_SCRIPT
    mock_generate.assert_called_once()
    called_interfaces = mock_generate.call_args[0][0]
    assert called_interfaces[0]["title"] == "获取用户列表"
    assert called_interfaces[0]["method"] == "GET"
    assert called_interfaces[0]["path"] == "/api/users"


@pytest.mark.django_db
@patch("apps.ai.views.generate_api_script", return_value=MOCK_SCRIPT)
def test_generate_api_script_saves_to_case(
    mock_generate: object,
    api_client: APIClient,
    user: User,
    project: Project,
) -> None:
    test_case = ApiTestCase.objects.create(
        project=project,
        title="获取用户列表",
        method="GET",
        path="/api/users",
        script="",
    )

    api_client.force_authenticate(user=user)
    response = api_client.post(
        "/api/ai/generate-api-script/",
        {"interfaces": SAMPLE_INTERFACES, "case_id": test_case.pk},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["case_id"] == test_case.pk

    test_case.refresh_from_db()
    assert test_case.script == MOCK_SCRIPT
    mock_generate.assert_called_once()


@pytest.mark.django_db
def test_generate_api_script_rejects_empty_interfaces(
    api_client: APIClient,
    user: User,
) -> None:
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/ai/generate-api-script/",
        {"interfaces": []},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@patch("apps.ai.views.generate_api_script", return_value=MOCK_SCRIPT)
def test_non_member_cannot_save_to_case(
    mock_generate: object,
    api_client: APIClient,
    user: User,
) -> None:
    owner = User.objects.create_user(username="owner", password="pass1234")
    project = Project.objects.create(name="Other", owner=owner)
    ProjectMember.objects.create(project=project, user=owner)
    test_case = ApiTestCase.objects.create(
        project=project,
        title="Private",
        method="GET",
        path="/api/private",
    )

    api_client.force_authenticate(user=user)
    response = api_client.post(
        "/api/ai/generate-api-script/",
        {"interfaces": SAMPLE_INTERFACES, "case_id": test_case.pk},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    test_case.refresh_from_db()
    assert test_case.script == ""


@pytest.mark.django_db
@patch(
    "apps.ai.views.generate_api_script",
    side_effect=LLMCallError("LLM 不可用"),
)
def test_generate_api_script_handles_llm_error(
    mock_generate: object,
    api_client: APIClient,
    user: User,
) -> None:
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/ai/generate-api-script/",
        {"interfaces": SAMPLE_INTERFACES},
        format="json",
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "LLM 不可用" in response.data["detail"]


@pytest.mark.django_db
def test_unauthenticated_request_is_denied(api_client: APIClient) -> None:
    response = api_client.post(
        "/api/ai/generate-api-script/",
        {"interfaces": SAMPLE_INTERFACES},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
