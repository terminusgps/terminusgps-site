import typing

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import validate_email
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, TemplateView
from terminusgps.authorizenet import profiles as anet_profiles
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import constants, utils
from terminusgps.wialon.items import WialonResource, WialonUser
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.models import Customer

from . import emails
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
    partial_template_name = "terminusgps/usage/partials/_commercial.html"
    template_name = "terminusgps/usage/commercial.html"


class TerminusgpsIndividualUseView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Individual Use", "subtitle": ""}
    http_method_names = ["get"]
    partial_template_name = "terminusgps/usage/partials/_individual.html"
    template_name = "terminusgps/usage/individual.html"


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
    template_name = "terminusgps/safety/teen.html"
    partial_template_name = "terminusgps/safety/partials/_teen.html"


class TerminusgpsSeniorSafetyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Senior Safety",
        "subtitle": "Tips and Tricks for Senior Drivers",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/safety/senior.html"
    partial_template_name = "terminusgps/safety/partials/_senior.html"


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


class TerminusgpsLoginView(HtmxTemplateResponseMixin, LoginView):
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker:dashboard")
    partial_template_name = "terminusgps/auth/partials/_login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("tracker:dashboard")
    template_name = "terminusgps/auth/login.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["username"].validators.append(validate_email)
        form.fields["username"].widget.attrs.update(
            **{
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "email@terminusgps.com",
                "autofocus": True,
                "inputmode": "email",
                "enterkeyhint": "next",
            }
        )
        form.fields["password"].widget.attrs.update(
            **{
                "class": settings.DEFAULT_FIELD_CLASS,
                "enterkeyhint": "done",
                "autocomplete": False,
            }
        )
        return form

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        if self.request.GET.get("username"):
            initial["username"] = self.request.GET.get("username")
        return initial


class TerminusgpsLogoutView(HtmxTemplateResponseMixin, LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post", "options"]
    next_page = reverse_lazy("login")
    partial_template_name = "terminusgps/auth/partials/_logout.html"
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    template_name = "terminusgps/auth/logout.html"


class TerminusgpsRegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
    }
    form_class = TerminusgpsRegisterForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps/auth/register.html"
    partial_template_name = "terminusgps/auth/partials/_register.html"
    success_url = reverse_lazy("tracker:dashboard")

    @transaction.atomic
    def form_valid(
        self, form: TerminusgpsRegisterForm
    ) -> HttpResponse | HttpResponseRedirect:
        user = get_user_model().objects.create_user(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            email=form.cleaned_data["username"],
        )
        customer = Customer.objects.create(user=user)
        customer = self.wialon_create_customer_objects(form, customer)
        customer = self.authorizenet_create_customer_profile(form, customer)
        customer.save()
        emails.send_registration_email(customer)
        return super().form_valid(form=form)

    @staticmethod
    @transaction.atomic
    def authorizenet_create_customer_profile(
        form: TerminusgpsRegisterForm, customer: Customer
    ) -> Customer:
        """
        Creates a customer profile in Authorizenet and saves its id to the customer.

        :param form: A Terminus GPS registration form.
        :type form: :py:obj:`~terminusgps_tracker.forms.TerminusgpsRegisterForm`
        :param customer: A customer object.
        :type customer: :py:obj:`~terminusgps_tracker.models.customers.Customer`
        :returns: A customer object with :py:attr:`authorizenet_id` set.
        :rtype: :py:obj:`~terminusgps_tracker.models.customers.Customer`

        """
        email, first_name, last_name = (
            str(form.cleaned_data["username"]),
            str(form.cleaned_data["first_name"]),
            str(form.cleaned_data["last_name"]),
        )

        response = anet_profiles.create_customer_profile(
            merchant_id=customer.pk,
            email=email,
            description=f"{first_name} {last_name}",
        )
        customer.authorizenet_profile_id = int(response.customerProfileId)
        return customer

    @staticmethod
    @transaction.atomic
    def wialon_create_customer_objects(
        form: TerminusgpsRegisterForm, customer: Customer
    ) -> Customer:
        """
        Creates Wialon objects and saves their ids to the customer.

        :param form: A Terminus GPS registration form.
        :type form: :py:obj:`~terminusgps_tracker.forms.TerminusgpsRegisterForm`
        :param customer: A customer object.
        :type customer: :py:obj:`~terminusgps_tracker.models.customers.Customer`
        :returns: A customer object with :py:attr:`end_user_id` and :py:attr:`resource_id` set.
        :rtype: :py:obj:`tuple`

        """
        username: str = form.cleaned_data["username"]
        password: str = form.cleaned_data["password1"]

        with WialonSession() as session:
            super_user = WialonUser(
                id=None,
                session=session,
                creator_id=settings.WIALON_ADMIN_ID,
                name=f"super_{username}",  # super_email@domain.com
                password=utils.generate_wialon_password(),
            )
            resource = WialonResource(
                id=None,
                session=session,
                creator_id=super_user.id,
                name=f"account_{username}",  # account_email@domain.com
            )
            end_user = WialonUser(
                id=None,
                session=session,
                creator_id=super_user.id,
                name=username,  # email@domain.com
                password=password,
            )

            end_user.grant_access(
                resource, access_mask=constants.ACCESSMASK_RESOURCE_BASIC
            )
            resource.create_account("terminusgps_ext_hist")
            resource.enable_account()
            resource.set_settings_flags()
            resource.disable_account()

            customer.wialon_user_id = end_user.id
            customer.wialon_resource_id = resource.id
            return customer
