from .auth import TrackerLogoutView, TrackerLoginView, TrackerSignupView
from .addresses import (
    ShippingAddressCreateView,
    ShippingAddressDeleteView,
    ShippingAddressDetailView,
)
from .assets import (
    AssetCreateView,
    AssetDeleteView,
    AssetDetailView,
    AssetListView,
    AssetRemoteView,
    AssetUpdateView,
)
from .profile import TrackerProfileSettingsView, TrackerProfileView
from .public import (
    TrackerAboutView,
    TrackerBugReportView,
    TrackerContactView,
    TrackerLandingView,
    TrackerPrivacyView,
    TrackerSourceView,
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
from .staff import EmailTemplateUploadView
