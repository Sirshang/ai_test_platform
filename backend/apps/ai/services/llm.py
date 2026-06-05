import logging
import os
from dataclasses import dataclass
from typing import Any

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class LLMCallError(Exception):
    """LLM 调用失败。"""


class LLMConfigError(LLMCallError):
    """LLM 配置无效。"""


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    api_key: str
    model: str
    fallback_model: str
    base_url: str | None


def _load_config() -> LLMConfig:
    api_key = os.environ.get("LLM_API_KEY", "").strip()
    if not api_key:
        raise LLMConfigError("LLM_API_KEY 未配置，无法调用 LLM。")

    provider = os.environ.get("LLM_PROVIDER", "openai").strip().lower()
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini").strip()
    fallback_model = os.environ.get("LLM_FALLBACK_MODEL", "gpt-4o-mini").strip()
    base_url = os.environ.get("LLM_BASE_URL", "").strip() or None

    return LLMConfig(
        provider=provider,
        api_key=api_key,
        model=model,
        fallback_model=fallback_model,
        base_url=base_url,
    )


def _create_chat_model(config: LLMConfig, model_name: str) -> Any:
    if config.provider == "openai":
        from langchain_openai import ChatOpenAI

        kwargs: dict[str, Any] = {
            "model": model_name,
            "api_key": config.api_key,
            "temperature": 0,
        }
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return ChatOpenAI(**kwargs)

    raise LLMConfigError(f"不支持的 LLM 类型：{config.provider}")


def _extract_content(response: Any) -> str:
    content = getattr(response, "content", response)
    if not isinstance(content, str):
        raise LLMCallError("LLM 返回内容格式无效。")
    text = content.strip()
    if not text:
        raise LLMCallError("LLM 返回了空内容。")
    return text


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(Exception),
)
def _invoke_model(llm: Any, prompt: str) -> str:
    response = llm.invoke(prompt)
    return _extract_content(response)


def _call_with_model(prompt: str, config: LLMConfig, model_name: str) -> str:
    llm = _create_chat_model(config, model_name)
    return _invoke_model(llm, prompt)


def call_llm(prompt: str) -> str:
    """调用 LLM 并返回文本结果，主模型失败时自动降级到备用模型。"""
    if not prompt.strip():
        raise LLMCallError("prompt 不能为空。")

    config = _load_config()
    models_to_try = [config.model]
    if config.fallback_model not in models_to_try:
        models_to_try.append(config.fallback_model)

    last_error: Exception | None = None
    for model_name in models_to_try:
        try:
            return _call_with_model(prompt, config, model_name)
        except Exception as exc:
            last_error = exc
            logger.warning(
                "LLM 调用失败，model=%s, provider=%s, error=%s",
                model_name,
                config.provider,
                exc,
            )

    raise LLMCallError(f"所有 LLM 模型均调用失败：{last_error}") from last_error
