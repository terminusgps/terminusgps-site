from django.urls import path

from . import views

urlpatterns = [
    path("auth/", views.auth, name="authorization"),
    path("create/", views.create_payment, name="create payment"),
    path("edit/<int:payment_id>/", views.edit_payment, name="create payment"),
    path("cancel/<int:payment_id>/", views.cancel_payment, name="create payment"),
    path("info/<int:payment_id>/", views.info, name="info"),
]
