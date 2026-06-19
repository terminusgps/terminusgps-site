from django.urls import path

from . import views

app_name = "terminusgps_installer"
urlpatterns = [
    path("", views.home_view, name="home"),
    path("jobs/", views.job_list_view, name="job list"),
    path("jobs/form/", views.new_job_form_view, name="new job form"),
    path("jobs/success/", views.new_job_success_view, name="new job success"),
    path(
        "/select-resource/", views.select_resource_view, name="select resource"
    ),
]
