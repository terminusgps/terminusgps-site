import terminusgps_payments
from django.urls import path, reverse_lazy
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "terminusgps_manager"
urlpatterns = [
    path(
        "dashboard/",
        views.TerminusGPSManagerTemplateView.as_view(
            template_name="terminusgps_manager/dashboard.html",
            extra_context={"title": "Dashboard"},
        ),
        name="dashboard",
    ),
    path(
        "account/",
        views.TerminusGPSManagerTemplateView.as_view(
            template_name="terminusgps_manager/account.html",
            extra_context={"title": "Account"},
        ),
        name="account",
    ),
    path(
        "subscriptions/",
        views.TerminusGPSManagerTemplateView.as_view(
            template_name="terminusgps_manager/subscriptions.html",
            extra_context={"title": "Subscription"},
        ),
        name="subscriptions",
    ),
    path(
        "subscriptions/new/",
        views.TerminusGPSManagerSubscriptionCreateView.as_view(
            template_name="terminusgps_payments/subscription_create.html",
            name=_("Terminus GPS Subscription"),
            success_url=reverse_lazy(
                "terminusgps_manager:create subscriptions success"
            ),
        ),
        name="create subscriptions",
    ),
    path(
        "subscriptions/new/success/",
        views.SubscriptionCreateSuccessView.as_view(),
        name="create subscriptions success",
    ),
    path(
        "subscriptions/<int:pk>/update/",
        terminusgps_payments.views.SubscriptionUpdateView.as_view(
            template_name="terminusgps_payments/subscription_update.html"
        ),
        name="update subscriptions",
    ),
    path(
        "subscriptions/<int:pk>/delete/",
        views.TerminusGPSManagerSubscriptionDeleteView.as_view(
            template_name="terminusgps_payments/subscription_delete.html"
        ),
        name="delete subscriptions",
    ),
]
