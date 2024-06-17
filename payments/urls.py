from django.urls import path

from . import views

urlpatterns = [
    path("qb/consent/", views.quickbooks_consent, name="quickbooks consent"),
    path("qb/auth/", views.quickbooks_auth, name="quickbooks authorization"),
    path("create/", views.create_payment, name="create payment"),
    path("edit/<int:payment_id>/", views.edit_payment, name="create payment"),
    path("cancel/<int:payment_id>/", views.cancel_payment, name="create payment"),
]
