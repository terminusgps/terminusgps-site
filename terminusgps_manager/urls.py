from django.urls import path

from . import views

# fmt: off
app_name = "terminusgps_manager"
urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("account/", views.AccountView.as_view(), name="account"),
]
