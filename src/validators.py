from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_username_exists(value: str) -> None:
    """Raises :py:exec:`~django.core.exceptions.ValidationError` if the value is not an email address for an existing user."""
    try:
        get_user_model().objects.get(username=value)
    except get_user_model().DoesNotExist:
        raise ValidationError(
            _("Whoops! Couldn't find a user with email '%(value)s', they don't exist."),
            code="invalid",
            params={"value": value},
        )
