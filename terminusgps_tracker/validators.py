from typing import Callable

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.models.asset import WialonAsset
from terminusgps_tracker.models.service import AuthService


def service_type_validator_factory(expected_service_type: AuthService.ServiceType) -> Callable:
    def validate_service_type_func(value: str) -> None:
        token = AuthService.objects.get(id=value)
        if token.service_type != expected_service_type:
            raise ValidationError(
                _("Invalid service type '%(service_type)s'. Expected service type '%(expected_service_type)s'."),
                params={"service_type": token.service_type, "expected_service_type": expected_service_type}
            )

def item_type_validator_factory(expected_item_type: WialonAsset.ItemType) -> Callable[str, None]:
    def validate_item_type_func(value: str) -> None:
        """Checks if the given value is a valid item type."""
        unit = WialonAsset.objects.get(id=value)
        if unit.item_type != expected_item_type:
            raise ValidationError(
                _("Invalid item type '%(item_type)s'. Asset must be item type '%(expected_item_type)s'."),
                params={"item_type": unit.item_type, "expected_item_type": expected_item_type}
            )
        return None
    return validate_item_type_func

def validate_item_type_user(value: str) -> None:
    """Checks if the given value is a valid user item type."""
    return item_type_validator_factory(WialonAsset.ItemType.USER)(value)

def validate_item_type_unit(value: str) -> None:
    """Checks if the given value is a valid unit item type."""
    return item_type_validator_factory(WialonAsset.ItemType.UNIT)(value)

def validate_service_type_wialon(value: str) -> None:
    """Checks if the given value is a valid Wialon service type."""
    return service_type_validator_factory(AuthService.ServiceType.WIALON)(value)
