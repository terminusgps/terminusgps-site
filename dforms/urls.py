from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("newsletter-signup/", views.newsletter_signup, name="newsletter signup"),
]
