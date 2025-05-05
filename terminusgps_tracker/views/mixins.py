import typing

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import ContextMixin


class TrackerAppConfigContextMixin(ContextMixin):
    """Adds the tracker app config to the view context."""

    def __init__(self, *args, **kwargs) -> None:
        """Raises :py:exec:`~django.core.exceptions.ImproperlyConfigured` if :confval:`TRACKER_APP_CONFIG` setting wasn't set."""
        if not hasattr(settings, "TRACKER_APP_CONFIG"):
            raise ImproperlyConfigured("'TRACKER_APP_CONFIG' setting is required.")
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds ``config`` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["config"] = settings.TRACKER_APP_CONFIG
        return context
