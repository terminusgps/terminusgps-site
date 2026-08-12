from django.urls import path

from . import views

app_name = "terminusgps_installer"
urlpatterns = [
    path("", views.home_view, name="home"),
    path("jobs/list/", views.job_list_view, name="job list"),
    path("jobs/form/", views.NewJobFormView.as_view(), name="new job form"),
    path(
        "jobs/<int:job_pk>/details/",
        views.job_details_view,
        name="job details",
    ),
    path(
        "units/<int:unit_pk>/exec_cmd/",
        views.execute_command_view,
        name="execute command",
    ),
    path(
        "units/<int:unit_pk>/cmds/",
        views.command_list_view,
        name="command list",
    ),
]
