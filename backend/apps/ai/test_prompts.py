from unittest.mock import patch

import pytest

from apps.ai.services.api_script import extract_python_code, generate_api_script
from apps.ai.services.prompts import (
    PromptTemplateError,
    build_api_gen_prompt,
    load_prompt_template,
)

SAMPLE_INTERFACE = [
    {
        "title": "获取用户列表",
        "method": "GET",
        "path": "/api/users",
        "description": "返回用户列表",
        "headers": {"Accept": "application/json"},
        "query_params": {"page": "1"},
        "body": "",
    }
]

MOCK_LLM_SCRIPT = """```python
def test_get_users_returns_200(api_client):
    response = api_client.get("/api/users", params={"page": 1})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
```"""


def test_load_api_gen_prompt_template() -> None:
    template = load_prompt_template("api_gen.txt")
    assert "{interfaces_json}" in template
    assert "api_client" in template
    assert "pytest" in template


def test_build_api_gen_prompt_includes_interface_json() -> None:
    prompt = build_api_gen_prompt(SAMPLE_INTERFACE)

    assert "获取用户列表" in prompt
    assert '"/api/users"' in prompt
    assert '"method": "GET"' in prompt
    assert "api_client" in prompt


def test_build_api_gen_prompt_rejects_empty_interfaces() -> None:
    with pytest.raises(PromptTemplateError, match="接口列表不能为空"):
        build_api_gen_prompt([])


def test_extract_python_code_strips_markdown() -> None:
    code = extract_python_code(MOCK_LLM_SCRIPT)

    assert "```" not in code
    assert code.startswith("def test_get_users_returns_200")
    assert "assert response.status_code == 200" in code


def test_extract_python_code_returns_plain_text() -> None:
    plain = 'def test_ping(api_client):\n    assert api_client.get("/ping").status_code == 200\n'
    assert extract_python_code(plain) == plain.strip()


@patch("apps.ai.services.api_script.call_llm", return_value=MOCK_LLM_SCRIPT)
def test_generate_api_script_returns_runnable_pytest_code(mock_call_llm: object) -> None:
    script = generate_api_script(SAMPLE_INTERFACE)

    assert "def test_get_users_returns_200(api_client):" in script
    assert "api_client.get(\"/api/users\"" in script
    assert "assert response.status_code == 200" in script
    mock_call_llm.assert_called_once()

    prompt = mock_call_llm.call_args[0][0]
    assert "/api/users" in prompt
