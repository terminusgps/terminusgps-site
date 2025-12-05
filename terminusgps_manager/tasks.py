from django.conf import settings
from django_tasks import task
from terminusgps.wialon.constants import ACCESSMASK_RESOURCE_BASIC
from terminusgps.wialon.flags import DataFlag
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import generate_wialon_password


@task
def wialon_account_registration_flow(
    username: str, password: str
) -> dict[str, dict[str, int]]:
    """
    Creates three Wialon macro-objects for the new user.

    Super user: A Wialon user with full access to the account.
    End user: A Wialon user with limited access rights to the account.
    Account: A Wialon resource transformed into an account.

    :param username: A Django user username.
    :type username: str
    :param password: A Django user password.
    :type password: str
    :returns: A dictionary of Wialon macro-object ids.
    :rtype: dict[str, dict[str, int]]

    """
    with WialonSession(token=settings.WIALON_TOKEN) as session:
        # Create super user
        super_user = session.wialon_api.core_create_user(
            **{
                "creatorId": settings.WIALON_ADMIN_ID,
                "name": f"super_{username}",
                "password": generate_wialon_password(),
                "dataFlags": DataFlag.USER_BASE,
            }
        )["item"]

        # Create resource
        resource = session.wialon_api.core_create_resource(
            **{
                "creatorId": super_user["id"],
                "name": f"account_{username}",
                "skipCreatorCheck": int(False),
                "dataFlags": DataFlag.RESOURCE_BASE,
            }
        )["item"]

        # Create account from resource
        session.wialon_api.account_create_account(
            **{"itemId": resource["id"], "plan": "terminusgps_ext_hist"}
        )

        # Create end user
        end_user = session.wialon_api.core_create_user(
            **{
                "creatorId": super_user["id"],
                "name": username,
                "password": password,
                "dataFlags": DataFlag.USER_BASE,
            }
        )["item"]

        # Grant end user access to account
        session.wialon_api.user_update_item_access(
            **{
                "userId": end_user["id"],
                "itemId": resource["id"],
                "accessMask": ACCESSMASK_RESOURCE_BASIC,
            }
        )

        # Disable the account (enabled by subscribing)
        session.wialon_api.account_enable_account(
            **{"itemId": resource["id"], "enable": int(False)}
        )

        return {
            "super_user": {"id": super_user["id"], "name": super_user["nm"]},
            "end_user": {"id": end_user["id"], "name": end_user["nm"]},
            "account": {"id": resource["id"], "name": resource["nm"]},
        }
