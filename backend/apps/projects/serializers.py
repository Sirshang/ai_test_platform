from rest_framework import serializers

from apps.projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "owner", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        name = value.strip()
        if not name:
            raise serializers.ValidationError("项目名称不能为空。")
        if len(name) > 100:
            raise serializers.ValidationError("项目名称不能超过 100 个字符。")
        return name
