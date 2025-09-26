from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, RedirectView, TemplateView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.items import WialonObjectFactory
from terminusgps.wialon.session import WialonAPIError, WialonSession
from terminusgps_payments.models import CustomerProfile
from terminusgps_payments.services import AuthorizenetService

from terminusgps_tracker.models import Customer

from .forms import TerminusgpsRegisterForm

if settings.configured and not hasattr(settings, "TRACKER_APP_CONFIG"):
    raise ImproperlyConfigured("'TRACKER_APP_CONFIG' setting is required.")


class TerminusgpsSourceCodeView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_APP_CONFIG.get("REPOSITORY_URL")


class TerminusgpsHostingView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_APP_CONFIG.get("HOSTING_URL")


class TerminusgpsCommercialUseView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Commercial Use", "subtitle": ""}
    http_method_names = ["get"]
    template_name = "terminusgps/commercial_use.html"
    partial_template_name = "terminusgps/partials/_commercial_use.html"


class TerminusgpsIndividualUseView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Individual Use", "subtitle": ""}
    http_method_names = ["get"]
    template_name = "terminusgps/individual_use.html"
    partial_template_name = "terminusgps/partials/_individual_use.html"


class TerminusgpsAboutView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "About", "subtitle": "Why we do what we do"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_about.html"
    template_name = "terminusgps/about.html"


class TerminusgpsContactView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Get in touch with us"}
    http_method_names = ["get"]
    template_name = "terminusgps/contact.html"
    partial_template_name = "terminusgps/partials/_contact.html"


class TerminusgpsHomeView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Home",
        "subtitle": settings.TRACKER_APP_CONFIG["MOTD"],
        "socials": settings.TRACKER_APP_CONFIG["SOCIALS"],
    }
    http_method_names = ["get"]
    template_name = "terminusgps/home.html"
    partial_template_name = "terminusgps/partials/_home.html"


class TerminusgpsTeenSafetyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Teen Safety",
        "subtitle": "Tips and Tricks for Teen Drivers",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/teen_safety.html"
    partial_template_name = "terminusgps/partials/_teen_safety.html"


class TerminusgpsSeniorSafetyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Senior Safety",
        "subtitle": "Tips and Tricks for Senior Drivers",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/senior_safety.html"
    partial_template_name = "terminusgps/partials/_senior_safety.html"


class TerminusgpsTermsAndConditionsView(
    HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Terms & Conditions",
        "subtitle": "You agree to these by using Terminus GPS services",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_terms.html"
    template_name = "terminusgps/terms.html"


class TerminusgpsFrequentlyAskedQuestionsView(
    HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Frequently Asked Questions",
        "subtitle": "You have questions, we have answers",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_faq.html"
    template_name = "terminusgps/faq.html"


class TerminusgpsPrivacyPolicyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Privacy Policy",
        "subtitle": "How we use your data",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_privacy.html"
    template_name = "terminusgps/privacy.html"


class TerminusgpsRegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
    }
    form_class = TerminusgpsRegisterForm
    partial_template_name = "registration/partials/_register.html"
    template_name = "registration/register.html"

    @transaction.atomic
    def form_valid(self, form: TerminusgpsRegisterForm) -> HttpResponse:
        try:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                customer = self.wialon_registration_flow(form, session)
            user = form.save(commit=True)
            user.email = form.cleaned_data["username"]
            customer.user = user
            customer.save()
            customer_profile = self.authorizenet_registration_flow(
                user, AuthorizenetService()
            )
            customer_profile.save()
            return super().form_valid(form=form)
        except WialonAPIError as e:
            form.add_error(
                None,
                ValidationError(
                    _("%(e)s"), code="invalid", params={"e": str(e)}
                ),
            )
            return self.form_invalid(form=form)
        except AuthorizenetControllerExecutionError as e:
            form.add_error(
                None,
                ValidationError(
                    _("%(code)s: %(message)s"),
                    code="invalid",
                    params={"code": e.code, "message": e.message},
                ),
            )
            return self.form_invalid(form=form)

    @transaction.atomic
    def wialon_registration_flow(
        self, form: TerminusgpsRegisterForm, session: WialonSession
    ) -> Customer:
        factory = WialonObjectFactory(session)
        user = factory.create(
            "user",
            creator_id=settings.WIALON_ADMIN_ID,
            name=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
        )
        resource = factory.create(
            "avl_resource",
            creator_id=getattr(user, "id"),
            name=f"account_{form.cleaned_data['username']}",
        )
        account = factory.create(
            "account",
            resource_id=getattr(resource, "id"),
            billing_plan="terminusgps_ext_hist",
        )
        account.deactivate()
        return Customer(
            wialon_resource_id=getattr(resource, "id"),
            wialon_user_id=getattr(user, "id"),
        )

    @transaction.atomic
    def authorizenet_registration_flow(
        self, user: User, service: AuthorizenetService
    ) -> CustomerProfile:
        customer_profile = CustomerProfile(user=user)
        anet_response = service.create_customer_profile(customer_profile)
        customer_profile.pk = int(anet_response.customerProfileId)
        return customer_profile
