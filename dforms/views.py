from django.shortcuts import render
from django.conf import settings

from .forms import RegistrationForm, NewsletterSignupForm

from .models import (
    RegistrationFormSubmission,
    NewsletterSignupSubmission,
)


def register(request):
    form = RegistrationForm()
    context = {
        "title": "Registration Form",
        "client": settings.CLIENT,
        "form": form,
    }

    return render(request, "dforms/register.html", context=context)


def newsletter_signup(request):
    form = NewsletterSignupForm()
    context = {
        "title": "Newsletter Signup Form",
        "client": settings.CLIENT,
    }

    if request.method == "POST":
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            NewsletterSignupSubmission.objects.create(
                email=form.cleaned_data["email"], opted_in=form.cleaned_data["opted_in"]
            ).save()

    context.update({"form": form})

    return render(request, "dforms/newsletter_signup.html", context=context)
