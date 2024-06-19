from django.urls import path

from . import views

urlpatterns = [path("auth/<str:service>/", views.authorize, name="authorize a service")]
