import json
from pathlib import Path
from typing import Any

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class PromptTemplateError(Exception):
    """Prompt 模板加载或渲染失败。"""


def load_prompt_template(template_name: str) -> str:
    template_path = PROMPTS_DIR / template_name
    if not template_path.is_file():
        raise PromptTemplateError(f"Prompt 模板不存在：{template_name}")
    return template_path.read_text(encoding="utf-8")


def render_prompt_template(template_name: str, **context: str) -> str:
    template = load_prompt_template(template_name)
    try:
        return template.format(**context)
    except KeyError as exc:
        raise PromptTemplateError(f"Prompt 模板缺少参数：{exc}") from exc


def build_api_gen_prompt(interfaces: list[dict[str, Any]]) -> str:
    if not interfaces:
        raise PromptTemplateError("接口列表不能为空。")

    interfaces_json = json.dumps(interfaces, ensure_ascii=False, indent=2)
    return render_prompt_template("api_gen.txt", interfaces_json=interfaces_json)
