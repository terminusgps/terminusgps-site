from django.urls import path

from . import views

# fmt: off
app_name = "terminusgps_manager"
urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("account/", views.AccountView.as_view(), name="account"),
    path("subscription/", views.SubscriptionView.as_view(), name="subscription"),
    path("subscription/create/", views.SubscriptionCreateView.as_view(), name="create subscription"),
    path("subscription/create/success/", views.SubscriptionCreateSuccessView.as_view(), name="create subscription success"),
]
