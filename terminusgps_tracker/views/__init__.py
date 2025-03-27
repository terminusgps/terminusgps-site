from .auth import TrackerLoginView, TrackerLogoutView, TrackerRegisterView
from .customers import (
    CustomerPaymentMethodCreateView,
    CustomerPaymentMethodDeleteView,
    CustomerPaymentMethodDetailView,
    CustomerPaymentMethodListView,
    CustomerShippingAddressCreateView,
    CustomerShippingAddressDeleteView,
    CustomerShippingAddressDetailView,
    CustomerShippingAddressListView,
)
from .generic import (
    TrackerAboutView,
    TrackerContactView,
    TrackerDashboardView,
    TrackerFrequentlyAskedQuestionsView,
    TrackerPrivacyPolicyView,
    TrackerSettingsView,
    TrackerSourceCodeView,
)
from .subscriptions import SubscriptionDetailView
