from django.urls import path

from . import views

urlpatterns = [
    path("profile/", views.TrackerProfileView.as_view(), name="tracker profile"),
    path(
        "password-reset/",
        views.TrackerProfileView.as_view(),
        name="tracker password reset",
    ),
    path("login/", views.TrackerLoginView.as_view(), name="tracker login"),
    path("logout/", views.TrackerLogoutView.as_view(), name="tracker logout"),
    path("register/", views.TrackerRegistrationView.as_view(), name="tracker register"),
    path("about/", views.TrackerAboutView.as_view(), name="tracker about"),
    path("contact/", views.TrackerContactView.as_view(), name="tracker contact"),
    path("source/", views.TrackerSourceView.as_view(), name="tracker source"),
    path("privacy/", views.TrackerPrivacyView.as_view(), name="tracker privacy"),
    path("forms/success/", views.FormSuccessView.as_view(), name="form success"),
    path("upload/asset/", views.AssetUploadView.as_view(), name="upload asset"),
    path(
        "upload/payment/", views.CreditCardUploadView.as_view(), name="upload payment"
    ),
    path("search_address/", views.SearchAddressView.as_view(), name="search address"),
]
