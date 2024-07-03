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
        "forms/register/",
        views.RegistrationFormView.as_view(),
        name="registration form",
    ),
]
