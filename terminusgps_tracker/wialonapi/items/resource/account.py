from wialon.api import WialonError

from terminusgps_tracker.wialonapi.items.base import WialonBase
from terminusgps_tracker.wialonapi.items.unit import WialonUnit

class WialonAccount(WialonBase):
    def create(self, **kwargs) -> None:
        if kwargs.get("resource", None) is None:
            raise ValueError("Tried to create an account but resource none.")
        if kwargs.get("user", None) is None:
            raise ValueError("Tried to create an account but user was none.")
        
        try:
            plan = kwargs.get("plan", None) if kwargs.get("plan", None) is not None else "terminusgps_ext_hist"
            self.session.wialon_api.account_create_account(**{
                "itemId": kwargs["resource"].id,
                "plan": plan,
            })
        except WialonError as e:
            raise e

    def migrate_unit(self, unit: WialonUnit) -> None:
        try:
            self.migrate_item(unit)
        except WialonError as e:
            raise e

    def migrate_item(self, item: WialonBase) -> None:
        try:
            self.session.wialon_api.account_change_account(**{
                "itemId": item.id,
                "resourceId": self.id,
            })
        except WialonError as e:
            raise e

    def enable(self) -> None:
        """Enables this account in Wialon."""
        try:
            self.session.wialon_api.account_enable_account(**{
                "itemId": self.id,
                "enable": int(True),
            })
        except WialonError as e:
            raise e

    def disable(self) -> None:
        """Disables this account in Wialon."""
        try:
            self.session.wialon_api.account_enable_account(**{
                "itemId": self.id,
                "enable": int(False),
            })
        except WialonError as e:
            raise e

    def enable_dealer_rights(self) -> None:
        try:
            self.session.wialon_api.account_update_dealer_rights(**{
                "itemId": self.id,
                "enable": True,
            })
        except WialonError as e:
            raise e

    def disable_dealer_rights(self) -> None:
        try:
            self.session.wialon_api.account_update_dealer_rights(**{
                "itemId": self.id,
                "enable": False,
            })
        except WialonError as e:
            raise e
