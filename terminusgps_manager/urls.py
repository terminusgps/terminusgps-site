from django.urls import path

from . import views

app_name = "terminusgps_manager"
urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("account/", views.AccountView.as_view(), name="account"),
    path(
        "subscriptions/",
        views.SubscriptionView.as_view(),
        name="subscriptions",
    ),
    path(
        "subscriptions/create/",
        views.SubscriptionCreateView.as_view(),
        name="create subscriptions",
    ),
    path(
        "subscriptions/<int:subscription_pk>/detail/",
        views.SubscriptionDetailView.as_view(),
        name="detail subscriptions",
    ),
    path(
        "subscriptions/<int:subscription_pk>/cancel/",
        views.SubscriptionCancelView.as_view(),
        name="cancel subscriptions",
    ),
    path(
        "subscriptions/<int:subscription_pk>/update/",
        views.SubscriptionUpdateView.as_view(),
        name="update subscriptions",
    ),
]
