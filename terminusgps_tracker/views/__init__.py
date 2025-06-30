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
    CustomerWialonUnitsView,
)
from .payments import (
    CustomerPaymentMethodCreateView,
    CustomerPaymentMethodDeleteView,
    CustomerPaymentMethodDetailView,
    CustomerPaymentMethodListView,
)
from .subscriptions import (
    SubscriptionCreateView,
    SubscriptionDeleteView,
    SubscriptionDetailView,
    SubscriptionItemListView,
    SubscriptionTransactionDetailView,
    SubscriptionTransactionsView,
    SubscriptionUpdateView,
)
from .units import (
    CustomerWialonUnitCreateView,
    CustomerWialonUnitDetailView,
    CustomerWialonUnitListDetailView,
    CustomerWialonUnitListUpdateView,
    CustomerWialonUnitListView,
)
