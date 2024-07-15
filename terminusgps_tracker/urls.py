from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("auth/<str:service>/", views.auth, name="auth"),
    path(
        "oauth2_callback/<str:service>/", views.oauth2_callback, name="oauth2 callback"
    ),
    path("search/", views.search, name="search"),
    path("search/wialon/", views.search_wialon, name="search wialon"),
    path(
        "forms/registration/",
        views.form_registration,
        name="form registration",
    ),
    path("forms/success/", views.form_success_view, name="form success"),
    path("creds/", views.forms.credentials_email_view, name="credentials email"),
]
