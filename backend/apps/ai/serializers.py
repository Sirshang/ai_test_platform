from rest_framework import serializers

ALLOWED_HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}


class InterfaceSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    method = serializers.CharField(max_length=10)
    path = serializers.CharField(max_length=500)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    headers = serializers.JSONField(required=False, default=dict)
    query_params = serializers.JSONField(required=False, default=dict)
    body = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_title(self, value: str) -> str:
        title = value.strip()
        if not title:
            raise serializers.ValidationError("接口标题不能为空。")
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

    def validate_headers(self, value: object) -> dict:
        if not isinstance(value, dict):
            raise serializers.ValidationError("headers 必须是 JSON 对象。")
        return value

    def validate_query_params(self, value: object) -> dict:
        if not isinstance(value, dict):
            raise serializers.ValidationError("query_params 必须是 JSON 对象。")
        return value


class GenerateApiScriptSerializer(serializers.Serializer):
    interfaces = InterfaceSerializer(many=True)
    case_id = serializers.IntegerField(required=False, min_value=1)

    def validate_interfaces(self, value: list[dict]) -> list[dict]:
        if not value:
            raise serializers.ValidationError("接口列表不能为空。")
        return value
