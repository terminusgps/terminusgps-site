from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .api import WialonSession, WialonUnit


def validate_wialon_imei(imei: str) -> None:
    if len(imei) > 17:
        raise ValidationError(_("IMEI # must be less than 18 characters."))
    if not imei.isdigit():
        raise ValidationError(_("IMEI # must be a number."))
    with WialonSession() as session:
        unit = WialonUnit(session, imei=imei)

        if unit.id is None:
            raise ValidationError(_("Your IMEI # was not found in our database"))
