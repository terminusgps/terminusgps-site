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
    view = models.CharField(max_length=512)
    is_complete = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.label

    @property
    def url(self) -> str:
        return reverse(self.view)


class TodoList(models.Model):
    items = models.ManyToManyField(TodoItem)

    def __str__(self) -> str:
        return f"To-Do List #{self.pk}"


class TrackerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    subscription = models.OneToOneField(
        "TrackerSubscription",
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
    )
    todo_list = models.OneToOneField(
        "TodoList", on_delete=models.CASCADE, default=None, blank=True, null=True
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

    def save(self, **kwargs) -> None:
        if not self.todo_list:
            todos = (
                TodoItem.objects.create(
                    label="Register your first asset", view="profile assets"
                ),
                TodoItem.objects.create(
                    label="Upload a payment method", view="profile payments"
                ),
                TodoItem.objects.create(
                    label="Select a subscription", view="profile subscription"
                ),
            )
            todo_list = TodoList.objects.create()
            todo_list.items.set(todos)
            self.todo_list = todo_list
        super().save(**kwargs)

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
