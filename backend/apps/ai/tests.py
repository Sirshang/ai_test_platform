import os
from unittest.mock import MagicMock, patch

import pytest

from apps.ai.services.llm import LLMCallError, LLMConfigError, call_llm


@pytest.fixture
def llm_env() -> dict[str, str]:
    return {
        "LLM_API_KEY": "test-api-key",
        "LLM_PROVIDER": "openai",
        "LLM_MODEL": "gpt-4o",
        "LLM_FALLBACK_MODEL": "gpt-4o-mini",
    }


def test_call_llm_returns_python_code(llm_env: dict[str, str]) -> None:
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content='print("hello world")'
    )

    with patch.dict(os.environ, llm_env, clear=False):
        with patch("apps.ai.services.llm._create_chat_model", return_value=mock_llm):
            result = call_llm("返回 hello world Python")

    assert 'print("hello world")' in result
    mock_llm.invoke.assert_called_once_with("返回 hello world Python")


def test_call_llm_raises_when_api_key_missing() -> None:
    env = os.environ.copy()
    env.pop("LLM_API_KEY", None)

    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(LLMConfigError, match="LLM_API_KEY"):
            call_llm("test")


def test_call_llm_falls_back_to_secondary_model(llm_env: dict[str, str]) -> None:
    primary_llm = MagicMock()
    primary_llm.invoke.side_effect = RuntimeError("primary failed")

    fallback_llm = MagicMock()
    fallback_llm.invoke.return_value = MagicMock(
        content="def test_hello():\n    assert True\n"
    )

    def fake_create_chat_model(config: object, model_name: str) -> MagicMock:
        if model_name == "gpt-4o":
            return primary_llm
        return fallback_llm

    with patch.dict(os.environ, llm_env, clear=False):
        with patch(
            "apps.ai.services.llm._create_chat_model",
            side_effect=fake_create_chat_model,
        ):
            result = call_llm("返回 pytest 代码")

    assert "def test_hello" in result
    fallback_llm.invoke.assert_called_once()


def test_call_llm_raises_when_all_models_fail(llm_env: dict[str, str]) -> None:
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = RuntimeError("network error")

    with patch.dict(os.environ, llm_env, clear=False):
        with patch("apps.ai.services.llm._create_chat_model", return_value=mock_llm):
            with pytest.raises(LLMCallError, match="所有 LLM 模型均调用失败"):
                call_llm("test prompt")


def test_call_llm_raises_on_empty_prompt(llm_env: dict[str, str]) -> None:
    with patch.dict(os.environ, llm_env, clear=False):
        with pytest.raises(LLMCallError, match="prompt 不能为空"):
            call_llm("   ")
