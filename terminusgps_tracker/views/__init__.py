from .auth import (
    TrackerLogoutView,
    TrackerLoginView,
    TrackerSignupView,
    TrackerRegistrationView,
)
from .addresses import (
    ShippingAddressCreateView,
    ShippingAddressDeleteView,
    ShippingAddressDetailView,
)
from .assets import (
    TrackerAssetCreateView,
    TrackerAssetDetailView,
    TrackerAssetUpdateView,
    TrackerAssetListView,
)
from .profile import TrackerProfileSettingsView, TrackerProfileView
from .public import (
    TrackerAboutView,
    TrackerContactView,
    TrackerLandingView,
    TrackerPrivacyView,
    TrackerSourceView,
    TrackerMapView,
    WialonAddressSearchView,
)
from .subscriptions import (
    TrackerSubscriptionUpdateView,
    TrackerSubscriptionDetailView,
    TrackerSubscriptionCancelView,
)
from .subscription_tiers import (
    TrackerSubscriptionTierUpdateView,
    TrackerSubscriptionTierCreateView,
    TrackerSubscriptionTierDeleteView,
    TrackerSubscriptionTierDetailView,
    TrackerSubscriptionTierListView,
)
from .payments import (
    PaymentMethodDetailView,
    PaymentMethodCreateView,
    PaymentMethodDeleteView,
)
