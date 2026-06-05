import pytest
from django.contrib import admin
from django.contrib.auth.models import User

from apps.users.admin import UserProfileAdmin
from apps.users.models import UserProfile


@pytest.mark.django_db
def test_user_profile_created_with_user() -> None:
    user = User.objects.create_user(username="alice", password="pass")

    assert UserProfile.objects.filter(user=user).exists()
    profile = user.profile
    assert profile.dingtalk_id == ""


@pytest.mark.django_db
def test_user_profile_dingtalk_id_can_be_updated() -> None:
    user = User.objects.create_user(username="bob", password="pass")
    profile = user.profile
    profile.dingtalk_id = "dt_123456"
    profile.save()

    profile.refresh_from_db()
    assert profile.dingtalk_id == "dt_123456"


@pytest.mark.django_db
def test_user_profile_registered_in_admin() -> None:
    assert admin.site.is_registered(UserProfile)
    assert isinstance(admin.site._registry[UserProfile], UserProfileAdmin)
