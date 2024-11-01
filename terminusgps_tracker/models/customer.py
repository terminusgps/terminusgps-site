from django.db import models
from django.contrib.auth import get_user_model

from authorizenet.apicontractsv1 import deleteCustomerProfileRequest
from authorizenet.apicontrollers import deleteCustomerProfileController

from terminusgps_tracker.authorizenetapi.auth import get_merchant_auth
from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.items import (
    WialonUser,
    WialonUnitGroup,
    WialonResource,
)


class TodoItem(models.Model):
    label = models.CharField(max_length=128)
    url = models.URLField()
    completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.label


class CustomerTodoList(models.Model):
    profile = models.OneToOneField(
        "CustomerProfile", on_delete=models.CASCADE, related_name="todo_list"
    )
    items = models.ManyToManyField(TodoItem)

    def __str__(self) -> str:
        return f"{self.profile.user.username}'s To-Do List"


class CustomerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
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

    def delete(self, *args, **kwargs):
        if self.authorizenet_profile_id:
            self._delete_authorizenet_objects()
        if all(
            [
                self.wialon_user_id,
                self.wialon_super_user_id,
                self.wialon_group_id,
                self.wialon_resource_id,
            ]
        ):
            self._delete_wialon_objects()
        return super().delete(*args, **kwargs)

    def _delete_authorizenet_objects(self) -> None:
        if self.authorizenet_profile_id is not None:
            request = deleteCustomerProfileRequest(
                merchantAuthentication=get_merchant_auth(),
                customerProfileId=str(self.authorizenet_profile_id),
            )
            controller = deleteCustomerProfileController(request)
            controller.execute()

    def _delete_wialon_objects(self) -> None:
        with WialonSession() as session:
            WialonUser(id=str(self.wialon_user_id), session=session).delete()
            WialonUnitGroup(id=str(self.wialon_group_id), session=session).delete()
            WialonResource(id=str(self.wialon_resource_id), session=session).delete()
            WialonUser(id=str(self.wialon_super_user_id), session=session).delete()

    @property
    def merchantCustomerId(self) -> str:
        return str(self.user.pk)
