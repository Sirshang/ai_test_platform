import json
from typing import Any

import yaml
from rest_framework import serializers

from apps.apitest.models import ApiTestCase
from apps.projects.models import Project

HTTP_METHODS = frozenset({"get", "post", "put", "patch", "delete", "head", "options"})


class SwaggerParseError(ValueError):
    """Swagger/OpenAPI 文档解析失败。"""


def parse_content_string(content: str, fmt: str | None = None) -> dict[str, Any]:
    text = content.strip()
    if not text:
        raise SwaggerParseError("Swagger 文档内容不能为空。")

    try:
        if fmt == "yaml":
            parsed = yaml.safe_load(text)
        elif fmt == "json":
            parsed = json.loads(text)
        elif text.startswith("{"):
            parsed = json.loads(text)
        else:
            parsed = yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise SwaggerParseError("Swagger 文档解析失败，请检查 JSON/YAML 格式。") from exc

    if not isinstance(parsed, dict):
        raise SwaggerParseError("Swagger 文档格式无效，根节点必须是对象。")
    return parsed


def load_swagger_spec(data: dict[str, Any]) -> dict[str, Any]:
    if "spec" in data:
        spec = data["spec"]
        if not isinstance(spec, dict):
            raise serializers.ValidationError({"spec": "spec 必须是 JSON 对象。"})
        return spec

    if "content" in data:
        content = data["content"]
        fmt = data.get("format")
        if isinstance(content, dict):
            return content
        if isinstance(content, str):
            try:
                return parse_content_string(content, fmt)
            except SwaggerParseError as exc:
                raise serializers.ValidationError({"content": str(exc)}) from exc
        raise serializers.ValidationError({"content": "content 必须是字符串或 JSON 对象。"})

    if "paths" in data:
        return data

    raise serializers.ValidationError(
        "请提供 Swagger 文档：直接提交 spec 对象，或使用 content 字段。"
    )


def extract_endpoints(spec: dict[str, Any]) -> list[dict[str, str]]:
    paths = spec.get("paths")
    if not isinstance(paths, dict) or not paths:
        raise SwaggerParseError("未在文档中找到 paths 接口定义。")

    endpoints: list[dict[str, str]] = []
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            method_lower = method.lower()
            if method_lower not in HTTP_METHODS:
                continue
            if not isinstance(operation, dict):
                continue

            title = (
                operation.get("summary")
                or operation.get("operationId")
                or f"{method.upper()} {path}"
            )
            description = operation.get("description", "")
            endpoints.append(
                {
                    "method": method.upper(),
                    "path": path,
                    "title": str(title)[:200],
                    "description": str(description),
                }
            )
    return endpoints


def import_swagger_cases(project: Project, spec: dict[str, Any]) -> list[ApiTestCase]:
    endpoints = extract_endpoints(spec)
    if not endpoints:
        raise SwaggerParseError("未在文档中找到任何可导入的 HTTP 接口。")

    cases: list[ApiTestCase] = []
    for endpoint in endpoints:
        case = ApiTestCase.objects.create(
            project=project,
            title=endpoint["title"],
            description=endpoint["description"],
            status=ApiTestCase.DRAFT,
            method=endpoint["method"],
            path=endpoint["path"],
            script="",
        )
        cases.append(case)
    return cases
