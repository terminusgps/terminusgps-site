from django.urls import path

from . import views

urlpatterns = [
    path("accounts/profile/", views.TerminusProfileView.as_view(), name="profile"),
    path(
        "accounts/password-reset/",
        views.TerminusPasswordResetView.as_view(),
        name="password reset",
    ),
    path("accounts/login/", views.TerminusLoginView.as_view(), name="login"),
    path("accounts/logout/", views.TerminusLogoutView.as_view(), name="logout"),
    path(
        "accounts/register/", views.TerminusRegistrationView.as_view(), name="register"
    ),
    path("forms/success/", views.FormSuccessView.as_view(), name="form success"),
    path("upload/asset/", views.AssetUploadView.as_view(), name="upload asset"),
    path(
        "upload/payment/", views.CreditCardUploadView.as_view(), name="upload payment"
    ),
    path("search_address/", views.SearchAddress.as_view(), name="search address"),
]
