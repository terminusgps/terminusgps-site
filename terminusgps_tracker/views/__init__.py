from .addresses import (
    CustomerShippingAddressCreateView,
    CustomerShippingAddressDeleteView,
    CustomerShippingAddressDetailView,
    CustomerShippingAddressListView,
)
from .customers import (
    CustomerAccountView,
    CustomerDashboardView,
    CustomerPaymentMethodChoicesView,
    CustomerShippingAddressChoicesView,
    CustomerSubscriptionView,
    CustomerSupportView,
    CustomerTransactionListView,
    CustomerTransactionsView,
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
    SubscriptionTransactionsView,
    SubscriptionUpdateView,
)
from .units import (
    CustomerWialonUnitCreateView,
    CustomerWialonUnitDetailView,
    CustomerWialonUnitListDeleteView,
    CustomerWialonUnitListDetailView,
    CustomerWialonUnitListUpdateView,
    CustomerWialonUnitListView,
)
