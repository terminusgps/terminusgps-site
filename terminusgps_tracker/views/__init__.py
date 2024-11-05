from .profile import (
    TrackerProfileView,
    TrackerProfileSubscriptionView,
    TrackerProfilePaymentsView,
    TrackerProfileAssetsView,
)
from .forms import (
    FormSuccessView,
    AssetUploadView,
    CreditCardUploadView,
    SearchAddressView,
)
from .registration import TrackerLoginView, TrackerLogoutView, TrackerRegistrationView
from .generic import (
    TrackerAboutView,
    TrackerSourceView,
    TrackerContactView,
    TrackerPrivacyView,
    TrackerSubscriptionView,
)
