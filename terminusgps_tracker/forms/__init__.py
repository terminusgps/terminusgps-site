from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if settings.configured and not hasattr(settings, "DEFAULT_FIELD_CLASS"):
    raise ImproperlyConfigured("'DEFAULT_FIELD_CLASS' setting is required.")

from .addresses import CustomerShippingAddressCreationForm
from .payments import CustomerPaymentMethodCreationForm
from .subscriptions import SubscriptionCreationForm
