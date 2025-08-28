from .addresses import (
    CustomerShippingAddressCreateView,
    CustomerShippingAddressDeleteView,
    CustomerShippingAddressDetailView,
    CustomerShippingAddressListView,
)
from .customers import (
    CustomerAccountView,
    CustomerDashboardView,
    CustomerSubscriptionView,
    CustomerUnitsView,
)
from .payments import (
    CustomerPaymentMethodCreateView,
    CustomerPaymentMethodDeleteView,
    CustomerPaymentMethodDetailView,
    CustomerPaymentMethodListView,
)
from .subscriptions import (
    CustomerSubscriptionCreateView,
    CustomerSubscriptionDeleteView,
    CustomerSubscriptionDetailView,
    CustomerSubscriptionUpdateView,
)
from .units import (
    CustomerWialonUnitCreateView,
    CustomerWialonUnitDetailView,
    CustomerWialonUnitListView,
    CustomerWialonUnitUpdateView,
)
