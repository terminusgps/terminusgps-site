from django.db import models
from django.contrib.auth import get_user_model

from django.urls import reverse

from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.integrations.wialon.items import (
    WialonUser,
    WialonUnitGroup,
    WialonResource,
)


class TodoItem(models.Model):
    label = models.CharField(max_length=64)
    view = models.CharField(max_length=512, default="tracker profile")
    is_complete = models.BooleanField(default=False)
    todo_list = models.ForeignKey(
        "TodoList", on_delete=models.CASCADE, default=None, blank=True, null=True
    )

    def __str__(self) -> str:
        return self.label

    @property
    def url(self) -> str:
        return reverse(self.view)


class TodoList(models.Model):
    profile = models.OneToOneField(
        "TrackerProfile", on_delete=models.CASCADE, related_name="todo_list"
    )
    items = models.ManyToManyField(TodoItem)

    def __str__(self) -> str:
        return f"{self.profile.user.username}'s To-Do List"


class TrackerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    subscription = models.OneToOneField(
        "TrackerSubscription",
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
    )
    notifications = models.ManyToManyField("TrackerNotification")
    authorizenet_profile_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_user_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_super_user_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_group_id = models.PositiveBigIntegerField(
        unique=False, null=True, blank=True, default=None
    )
    wialon_resource_id = models.PositiveBigIntegerField(
        unique=False, null=True, blank=True, default=None
    )

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"

    def delete(
        self,
        delete_wialon_objs: bool = False,
        delete_authorizenet_objs: bool = False,
        using=None,
        keep_parents: bool = False,
        **kwargs,
    ) -> tuple[int, dict[str, int]]:
        if delete_wialon_objs:
            with WialonSession() as session:
                WialonUser(id=str(self.wialon_user_id), session=session).delete()
                WialonUnitGroup(id=str(self.wialon_group_id), session=session).delete()
                WialonResource(
                    id=str(self.wialon_resource_id), session=session
                ).delete()
                WialonUser(id=str(self.wialon_super_user_id), session=session).delete()
        if delete_authorizenet_objs:
            ...
        return super().delete(using=using, keep_parents=keep_parents, **kwargs)

    @property
    def merchantCustomerId(self) -> str:
        return str(self.user.pk)

    @property
    def customerProfileId(self) -> str:
        return str(self.authorizenet_profile_id)
