import pytest
from django.contrib.auth.models import User

from apps.apitest.models import ApiEnvironment, ApiTestCase
from apps.projects.models import Project


@pytest.mark.django_db
def test_create_two_api_environments_for_project() -> None:
    owner = User.objects.create_user(username="owner", password="pass")
    project = Project.objects.create(name="API Project", owner=owner)

    dev_env = ApiEnvironment.objects.create(
        project=project,
        name="开发环境",
        base_url="https://dev.example.com",
        headers={"Authorization": "Bearer dev-token"},
        variables={"env": "dev"},
    )
    prod_env = ApiEnvironment.objects.create(
        project=project,
        name="生产环境",
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer prod-token"},
        variables={"env": "prod"},
    )

    assert project.api_envs.count() == 2
    assert dev_env.headers == {"Authorization": "Bearer dev-token"}
    assert prod_env.variables == {"env": "prod"}
    assert dev_env.created_at is not None
    assert prod_env.updated_at is not None


@pytest.mark.django_db
def test_create_api_test_case() -> None:
    owner = User.objects.create_user(username="owner", password="pass")
    project = Project.objects.create(name="Case Project", owner=owner)

    test_case = ApiTestCase.objects.create(
        project=project,
        title="获取用户列表",
        description="验证用户列表接口返回 200",
        status=ApiTestCase.DRAFT,
        method="GET",
        path="/api/users",
        headers={"Accept": "application/json"},
        query_params={"page": "1"},
        body="",
        script="def test_users():\n    assert True\n",
    )

    assert ApiTestCase.objects.count() == 1
    assert test_case.project == project
    assert test_case.status == ApiTestCase.DRAFT
    assert test_case.method == "GET"
    assert test_case.path == "/api/users"
    assert test_case.script.startswith("def test_users")
    assert test_case.last_run_status is None
    assert test_case.last_run_at is None
