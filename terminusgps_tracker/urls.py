from django.urls import path

from . import views

urlpatterns = [
    path("", views.TrackerDashboardView.as_view(), name="dashboard"),
    path("login/", views.TrackerLoginView.as_view(), name="login"),
    path("logout/", views.TrackerLogoutView.as_view(), name="logout"),
    path("about/", views.TrackerAboutView.as_view(), name="about"),
    path("contact/", views.TrackerContactView.as_view(), name="contact"),
    path("privacy/", views.TrackerPrivacyPolicyView.as_view(), name="privacy"),
    path("register/", views.TrackerRegisterView.as_view(), name="register"),
    path("source/", views.TrackerSourceCodeView.as_view(), name="source code"),
    path("settings/", views.TrackerSettingsView.as_view(), name="settings"),
    path("faq/", views.TrackerFrequentlyAskedQuestionsView.as_view(), name="faq"),
    path(
        "payments/", views.CustomerPaymentMethodListView.as_view(), name="list payments"
    ),
    path(
        "payments/create/",
        views.CustomerPaymentMethodCreateView.as_view(),
        name="create payment",
    ),
    path(
        "payments/<int:pk>/",
        views.CustomerPaymentMethodDetailView.as_view(),
        name="detail payment",
    ),
    path(
        "payments/<int:pk>/delete/",
        views.CustomerPaymentMethodDeleteView.as_view(),
        name="delete payment",
    ),
    path(
        "addresses/",
        views.CustomerShippingAddressListView.as_view(),
        name="list addresses",
    ),
    path(
        "addresses/create/",
        views.CustomerShippingAddressCreateView.as_view(),
        name="create address",
    ),
    path(
        "addresses/<int:pk>/",
        views.CustomerShippingAddressDetailView.as_view(),
        name="detail address",
    ),
    path(
        "addresses/<int:pk>/delete/",
        views.CustomerShippingAddressDeleteView.as_view(),
        name="delete address",
    ),
    path(
        "subscription/<int:pk>/",
        views.SubscriptionDetailView.as_view(),
        name="detail subscription",
    ),
]
