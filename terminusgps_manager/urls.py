from django.urls import path

from . import views

app_name = "terminusgps_manager"
urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("contact/form/", views.contact_form_view, name="contact form"),
    path(
        "contact/form/success/",
        views.contact_form_success_view,
        name="contact form success",
    ),
]
