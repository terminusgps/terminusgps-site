from django.urls import path

from . import views

urlpatterns = [
    path("forms/<str:form_name>/", views.get_form, name="form"),
    path("fields/<str:field_name>/", views.get_field, name="field"),
]
