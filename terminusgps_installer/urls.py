from django.urls import path

from . import views

app_name = "terminusgps_installer"
urlpatterns = [
    path("", views.start_new_job_view, name="start new job"),
    path("jobs/new/form/", views.new_job_form_view, name="new job form"),
    path(
        "jobs/new/success/", views.new_job_success_view, name="new job success"
    ),
    path(
        "jobs/incomplete/", views.incomplete_jobs_view, name="incomplete jobs"
    ),
    path(
        "select-resource/", views.select_resource_view, name="select resource"
    ),
    path("vin-info/", views.vin_info_view, name="vin info"),
]
