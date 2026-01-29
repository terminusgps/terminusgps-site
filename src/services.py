from django.conf import settings
from django.db import transaction
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import generate_wialon_password

from terminusgps_manager.models import (
    TerminusGPSCustomer,
    WialonAccount,
    WialonUser,
)

from .forms import TerminusgpsRegistrationForm


@transaction.atomic
def wialon_registration_flow(
    form: TerminusgpsRegistrationForm, customer: TerminusGPSCustomer
) -> None:
    with WialonSession(token=settings.WIALON_TOKEN) as session:
        # Create account user
        super_user_data = session.wialon_api.core_create_user(
            **{
                "creatorId": settings.WIALON_ADMIN_ID,
                "name": f"super_{form.cleaned_data['username']}",
                "password": generate_wialon_password(),
                "dataFlags": 1,
            }
        )
        super_user = WialonUser()
        super_user.pk = int(super_user_data["item"]["id"])
        super_user.save()

        # Create resource
        resource_data = session.wialon_api.core_create_resource(
            **{
                "creatorId": super_user.pk,
                "name": f"account_{form.cleaned_data['username']}",
                "skipCreatorCheck": int(True),
                "dataFlags": 1,
            }
        )
        # Create account from resource
        session.wialon_api.account_create_account(
            **{
                "itemId": int(resource_data["item"]["id"]),
                "plan": "terminusgps_ext_hist",
            }
        )
        account = WialonAccount()
        account.pk = int(resource_data["item"]["id"])
        account.save()

        # Enable account and clear flags
        account.enable(session)
        account.update_flags(session, flags=-0x20)

        # Create end user
        end_user_data = session.wialon_api.core_create_user(
            **{
                "creatorId": super_user.pk,
                "name": form.cleaned_data["username"],
                "password": form.cleaned_data["password1"],
                "dataFlags": 1,
            }
        )
        end_user = WialonUser()
        end_user.pk = int(end_user_data["item"]["id"])
        end_user.save()

        # Disable account, enabled by subscribing
        account.disable(session)

        # Assign to objects to customer
        customer.wialon_user = end_user
        customer.wialon_account = account
        customer.save(update_fields=["wialon_user", "wialon_account"])
