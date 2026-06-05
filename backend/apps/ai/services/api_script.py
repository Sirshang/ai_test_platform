import re
from typing import Any

from apps.ai.services.llm import call_llm
from apps.ai.services.prompts import build_api_gen_prompt

_CODE_BLOCK_PATTERN = re.compile(r"```(?:python)?\s*\n?(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_python_code(raw_output: str) -> str:
    """去除 LLM 输出中可能包含的 markdown 代码块标记。"""
    text = raw_output.strip()
    match = _CODE_BLOCK_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return text


def generate_api_script(interfaces: list[dict[str, Any]]) -> str:
    """根据接口列表生成 pytest API 测试脚本。"""
    prompt = build_api_gen_prompt(interfaces)
    raw_output = call_llm(prompt)
    return extract_python_code(raw_output)
