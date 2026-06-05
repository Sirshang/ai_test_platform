from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.apitest.models import ApiTestCase


class IsApiCaseProjectMember(BasePermission):
    """仅允许已登录用户访问；对象级操作限制为所属项目成员。"""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Request, view: APIView, obj: ApiTestCase) -> bool:
        return obj.project.members.filter(user=request.user).exists()
