from django.urls import path
from . import views

urlpatterns = [
    path("inquiry/", views.TrackerEmailInquiryView.as_view(), name="email inquiry"),
    path(
        "render_map/<int:x>_<int:y>_<int:zoom>/<str:sid>/",
        views.TrackerMapView.as_view(),
        name="render map",
    ),
    path(
        "newsletter/new/",
        views.TrackerNewsletterSignupView.as_view(),
        name="newsletter signup",
    ),
    path(
        "emails/upload/",
        views.EmailTemplateUploadView.as_view(),
        name="upload email template",
    ),
    path(
        "emails/renderer/",
        views.EmailTemplateRendererView.as_view(),
        name="render email template",
    ),
    path("", views.TrackerLandingView.as_view(), name="tracker landing"),
    path("profile/", views.TrackerProfileView.as_view(), name="tracker profile"),
    path("register/", views.TrackerRegistrationView.as_view(), name="tracker register"),
    path("about/", views.TrackerAboutView.as_view(), name="tracker about"),
    path("contact/", views.TrackerContactView.as_view(), name="tracker contact"),
    path("source/", views.TrackerSourceView.as_view(), name="tracker source"),
    path("privacy/", views.TrackerPrivacyView.as_view(), name="tracker privacy"),
    path("login/", views.TrackerLoginView.as_view(), name="tracker login"),
    path("logout/", views.TrackerLogoutView.as_view(), name="tracker logout"),
    path("signup/", views.TrackerSignupView.as_view(), name="tracker signup"),
    path("assets/table/", views.AssetTableView.as_view(), name="asset table"),
    path("assets/new/", views.AssetCreateView.as_view(), name="asset create"),
    path("assets/<int:pk>/", views.AssetDetailView.as_view(), name="asset detail"),
    path(
        "assets/<int:pk>/remote/", views.AssetRemoteView.as_view(), name="asset remote"
    ),
    path(
        "assets/<int:pk>/update/", views.AssetUpdateView.as_view(), name="asset update"
    ),
    path(
        "subscriptions/",
        views.TrackerSubscriptionTierListView.as_view(),
        name="tracker subscriptions",
    ),
    path(
        "subscriptions/<int:pk>/",
        views.TrackerSubscriptionTierDetailView.as_view(),
        name="tier detail",
    ),
    path("profile/report/", views.TrackerBugReportView.as_view(), name="bug report"),
    path(
        "profile/subscription/<int:pk>/",
        views.TrackerSubscriptionDetailView.as_view(),
        name="subscription detail",
    ),
    path(
        "profile/subscription/<int:pk>/update/",
        views.TrackerSubscriptionUpdateView.as_view(),
        name="subscription update",
    ),
    path(
        "profile/subscription/<int:pk>/cancel/",
        views.TrackerSubscriptionCancelView.as_view(),
        name="subscription cancel",
    ),
    path(
        "profile/settings/", views.TrackerProfileSettingsView.as_view(), name="settings"
    ),
    path(
        "profile/shipping/new/",
        views.ShippingAddressCreateView.as_view(),
        name="create shipping",
    ),
    path(
        "profile/shipping/<int:pk>/",
        views.ShippingAddressDetailView.as_view(),
        name="detail shipping",
    ),
    path(
        "profile/shipping/<int:pk>/delete/",
        views.ShippingAddressDeleteView.as_view(),
        name="delete shipping",
    ),
    path(
        "profile/payments/new/",
        views.PaymentMethodCreateView.as_view(),
        name="create payment",
    ),
    path(
        "profile/payments/<int:pk>/",
        views.PaymentMethodDetailView.as_view(),
        name="detail payment",
    ),
    path(
        "profile/payments/<int:pk>/delete/",
        views.PaymentMethodDeleteView.as_view(),
        name="delete payment",
    ),
]
