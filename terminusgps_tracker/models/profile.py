from django.contrib.auth import get_user_model
from django.db import models
from django.db import transaction

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


class TrackerProfile(models.Model):
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

    def save(self, **kwargs) -> None:
        if not self.authorizenet_profile_id:
            create_request = self._generate_create_customer_profile_request(
                merchantAuthentication=get_merchant_auth()
            )
            self.authorizenet_profile_id = self._create_authorizenet_profile(
                create_request
            )

        if not self.wialon_user_id:
            with WialonSession() as session:
                self._create_wialon_objects(session=session)
        super().save(**kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        delete_request = self._generate_delete_customer_profile_request(
            merchantAuthentication=get_merchant_auth()
        )
        self._delete_authorizenet_profile(delete_request)
        self._delete_wialon_objects()
        return super().delete(*args, **kwargs)

    @transaction.atomic
    def complete_todo(self, view_name: str) -> None:
        todo_item = self.todo_list.todo_items.filter(view=view_name).first()
        if todo_item:
            todo_item.is_complete = True
            todo_item.save()

    @transaction.atomic
    def delete_todo(self, view_name: str) -> None:
        todo_item = self.todo_list.todo_items.filter(view=view_name).first()
        if todo_item:
            del todo_item

    def _delete_wialon_objects(self) -> None:
        with WialonSession() as session:
            end_user = WialonUser(id=str(self.wialon_user_id), session=session)
            end_user_group = WialonUnitGroup(
                id=str(self.wialon_group_id), session=session
            )
            end_user_resource = WialonResource(
                id=str(self.wialon_resource_id), session=session
            )
            super_user = WialonUser(id=str(self.wialon_super_user_id), session=session)

            end_user.delete()
            end_user_group.delete()
            end_user_resource.delete()
            super_user.delete()

    @property
    def merchantCustomerId(self) -> str:
        return str(self.user.pk)

    @property
    def customerProfileId(self) -> str:
        return str(self.authorizenet_profile_id)

    @property
    def firstName(self) -> str:
        return self.user.first_name

    @property
    def lastName(self) -> str:
        return self.user.last_name

    @property
    def fullName(self) -> str:
        return f"{self.firstName} {self.lastName}"

    def _create_wialon_objects(self, session: WialonSession) -> None:
        admin_user = WialonUser(id="27881459", session=session)
        super_user = WialonUser(
            owner=admin_user,
            name=f"super_{self.user.username}",
            password=self.user.password,
            session=session,
        )
        end_user = WialonUser(
            owner=super_user,
            name=self.user.username,
            password=self.user.password,
            session=session,
        )
        end_user_group = WialonUnitGroup(
            owner=super_user, name=f"group_{self.user.username}", session=session
        )
        end_user_resource = WialonResource(
            owner=super_user, name=f"resource_{self.user.username}", session=session
        )

        self.wialon_super_user_id = super_user.id
        self.wialon_user_id = end_user.id
        self.wialon_group_id = end_user_group.id
        self.wialon_resource_id = end_user_resource.id

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
