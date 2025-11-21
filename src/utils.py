import typing

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from terminusgps.wialon import constants
from terminusgps.wialon.flags import DataFlag
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import generate_wialon_password

from .forms import TerminusgpsRegistrationForm


def set_wialon_admin_field(
    item_id: int, key: str, value: str, session: WialonSession
) -> None:
    session.wialon_api.item_update_admin_field(
        **{
            "itemId": item_id,
            "id": 0,
            "callMode": "create",
            "n": key,
            "v": value,
        }
    )


def create_wialon_user(
    username: str,
    password: str,
    session: WialonSession,
    creator_id: str | None = None,
) -> dict[str, typing.Any]:
    if len(username) < 4:
        raise ValueError(
            f"Username cannot be less than 4 characters in length, got {len(username)}."
        )
    elif len(username) > 50:
        raise ValueError(
            f"Username cannot be greater than 50 characters in length, got {len(username)}."
        )
    return session.wialon_api.core_create_user(
        **{
            "creatorId": creator_id
            if creator_id is not None
            else settings.WIALON_ADMIN_ID,
            "name": username,
            "password": password,
            "dataFlags": DataFlag.USER_BASE,
        }
    )["item"]


def create_wialon_resource(
    name: str,
    session: WialonSession,
    creator_id: str | None = None,
    skip_creator_check: bool = False,
) -> dict[str, typing.Any]:
    if len(name) < 4:
        raise ValueError(
            f"Name cannot be less than 4 characters in length, got {len(name)}."
        )
    elif len(name) > 50:
        raise ValueError(
            f"Name cannot be greater than 50 characters in length, got {len(name)}."
        )
    return session.wialon_api.core_create_resource(
        **{
            "creatorId": creator_id
            if creator_id is not None
            else settings.WIALON_ADMIN_ID,
            "name": name,
            "dataFlags": DataFlag.RESOURCE_BASE,
            "skipCreatorCheck": int(skip_creator_check),
        }
    )["item"]


def create_wialon_account(
    resource_id: int,
    session: WialonSession,
    plan: str = "terminusgps_ext_hist",
) -> dict[str, typing.Any]:
    return session.wialon_api.account_create_account(
        **{"itemId": resource_id, "plan": plan}
    )


def grant_wialon_access(
    item_id: int, user_id: int, access_mask: int, session: WialonSession
) -> dict[str, typing.Any]:
    return session.wialon_api.user_update_item_access(
        **{"userId": user_id, "itemId": item_id, "accessMask": access_mask}
    )


def wialon_account_registration_flow(
    user: AbstractBaseUser,
    form: TerminusgpsRegistrationForm,
    session: WialonSession,
) -> None:
    """
    Creates three Wialon macro-objects for the new user.

    Super user: A Wialon user with full access to the account.
    End user: A Wialon user with limited access rights to the account.
    Account: A Wialon resource transformed into an account.

    """
    super_user = create_wialon_user(
        username=f"super_{form.cleaned_data['username']}",
        password=generate_wialon_password(),
        session=session,
    )
    resource = create_wialon_resource(
        name=f"account_{form.cleaned_data['username']}",
        creator_id=super_user["id"],
        session=session,
    )
    end_user = create_wialon_user(
        username=form.cleaned_data["username"],
        password=form.cleaned_data["password1"],
        session=session,
    )
    create_wialon_account(resource_id=resource["id"], session=session)
    grant_wialon_access(
        item_id=resource["id"],
        user_id=end_user["id"],
        access_mask=constants.ACCESSMASK_RESOURCE_BASIC,
        session=session,
    )
    set_wialon_admin_field(
        item_id=end_user["id"],
        key="django_user_pk",
        value=str(user.pk),
        session=session,
    )
