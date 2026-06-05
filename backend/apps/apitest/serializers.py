from rest_framework import serializers

from apps.apitest.models import ApiTestCase
from apps.projects.models import Project

ALLOWED_HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}


class ApiTestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiTestCase
        fields = [
            "id",
            "project",
            "title",
            "description",
            "status",
            "method",
            "path",
            "headers",
            "query_params",
            "body",
            "script",
            "last_run_status",
            "last_run_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "last_run_status",
            "last_run_at",
            "created_at",
            "updated_at",
        ]

    def validate_project(self, value: Project) -> Project:
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError("未认证用户无法指定项目。")
        if not value.members.filter(user=request.user).exists():
            raise serializers.ValidationError("您不是该项目的成员。")
        return value

    def validate_title(self, value: str) -> str:
        title = value.strip()
        if not title:
            raise serializers.ValidationError("用例标题不能为空。")
        if len(title) > 200:
            raise serializers.ValidationError("用例标题不能超过 200 个字符。")
        return title

    def validate_method(self, value: str) -> str:
        method = value.strip().upper()
        if method not in ALLOWED_HTTP_METHODS:
            raise serializers.ValidationError(f"不支持的 HTTP 方法：{value}")
        return method

    def validate_path(self, value: str) -> str:
        path = value.strip()
        if not path:
            raise serializers.ValidationError("请求路径不能为空。")
        if not path.startswith("/"):
            raise serializers.ValidationError("请求路径必须以 / 开头。")
        return path

    def validate_status(self, value: str) -> str:
        valid_statuses = {choice[0] for choice in ApiTestCase.STATUS_CHOICES}
        if value not in valid_statuses:
            raise serializers.ValidationError("无效的状态值。")
        return value

    def validate_headers(self, value: object) -> dict:
        if not isinstance(value, dict):
            raise serializers.ValidationError("headers 必须是 JSON 对象。")
        return value

    def validate_query_params(self, value: object) -> dict:
        if not isinstance(value, dict):
            raise serializers.ValidationError("query_params 必须是 JSON 对象。")
        return value


class ImportSwaggerSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, allow_blank=True)
    spec = serializers.JSONField(required=False)
    format = serializers.ChoiceField(choices=["json", "yaml"], required=False)
