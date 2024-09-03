from django.urls import path

from . import views

urlpatterns = [
    path("dash/", views.dashboard_view, name="dashboard"),
    path(
        "forms/registration/",
        views.RegistrationFormView.as_view(),
        name="registration form",
    ),
    path("docs/", views.documentation_index, name="documentation index"),
    path("docs/<str:page_name>/", views.documentation_view, name="documentation view"),
]
