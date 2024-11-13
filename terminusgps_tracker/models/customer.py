from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from authorizenet.apicontractsv1 import (
    customerProfileType,
    merchantAuthenticationType,
    createCustomerProfileRequest,
    createCustomerProfileResponse,
    deleteCustomerProfileRequest,
    deleteCustomerProfileResponse,
)
from authorizenet.apicontrollers import (
    createCustomerProfileController,
    deleteCustomerProfileController,
)

from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth
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
    todo_list = models.OneToOneField(
        "TodoList", on_delete=models.CASCADE, null=True, blank=True, default=None
    )
    notifications = models.ManyToManyField("TrackerNotification")
    subscription = models.OneToOneField(
        "TrackerSubscription",
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
    )

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
        if not self.authorizenet_profile_id:
            create_request = self._generate_create_customer_profile_request(
                merchantAuthentication=get_merchant_auth()
            )
            self.authorizenet_profile_id = self._create_authorizenet_profile(
                create_request
            )

        super().save(**kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        with WialonSession() as session:
            WialonUser(id=str(self.wialon_user_id), session=session).delete()
            WialonUnitGroup(id=str(self.wialon_group_id), session=session).delete()
            WialonResource(id=str(self.wialon_resource_id), session=session).delete()
            WialonUser(id=str(self.wialon_super_user_id), session=session).delete()

        delete_request = self._generate_delete_customer_profile_request(
            merchantAuthentication=get_merchant_auth()
        )
        self._delete_authorizenet_profile(delete_request)
        return super().delete(*args, **kwargs)

    @property
    def merchantCustomerId(self) -> str:
        return str(self.user.pk)

    @property
    def customerProfileId(self) -> str:
        return str(self.authorizenet_profile_id)

    def _create_authorizenet_profile(
        self, request: createCustomerProfileRequest
    ) -> str:
        controller = createCustomerProfileController(request)
        controller.execute()
        response: createCustomerProfileResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(
                f"Failed to properly create Authorize.NET customer profile: {response.messages.message[0]["text"].text}"
            )
        return response.customerProfileId

    def _delete_authorizenet_profile(
        self, request: deleteCustomerProfileRequest
    ) -> None:
        controller = deleteCustomerProfileController(request)
        controller.execute()
        response: deleteCustomerProfileResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(
                f"Failed to properly delete Authorize.NET customer profile: {response.messages.message[0]["text"].text}"
            )

    def _generate_delete_customer_profile_request(
        self, merchantAuthentication: merchantAuthenticationType
    ) -> dict:
        return deleteCustomerProfileRequest(
            merchantAuthentication=merchantAuthentication,
            customerProfileId=self.customerProfileId,
        )

    def _generate_create_customer_profile_request(
        self, merchantAuthentication: merchantAuthenticationType
    ) -> dict:
        return createCustomerProfileRequest(
            merchantAuthentication=merchantAuthentication,
            profile=customerProfileType(merchantCustomerId=self.merchantCustomerId),
        )
