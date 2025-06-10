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
    CustomerSupportView,
    CustomerTransactionListView,
    CustomerTransactionsView,
    CustomerWialonUnitCreateView,
    CustomerWialonUnitDetailView,
    CustomerWialonUnitListView,
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
    SubscriptionDetailView,
    SubscriptionPricingView,
    SubscriptionTierDetailView,
    SubscriptionTierListView,
    SubscriptionUpdateView,
)
