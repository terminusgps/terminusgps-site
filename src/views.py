import datetime

from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import validate_email
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, RedirectView, TemplateView
from terminusgps.authorizenet.profiles import CustomerProfile
from terminusgps.authorizenet.utils import get_days_between
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import constants, utils
from terminusgps.wialon.items import WialonResource, WialonUser
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.models import Customer

from .forms import TerminusgpsAuthenticationForm, TerminusgpsRegisterForm
from .validators import validate_username_exists

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


class TerminusgpsAboutView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "About",
        "subtitle": "Why Terminus GPS does what it does",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_about.html"
    template_name = "terminusgps/about.html"


class TerminusgpsContactView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Get in touch with us"}
    http_method_names = ["get"]
    template_name = "terminusgps/contact.html"
    partial_template_name = "terminusgps/partials/_contact.html"


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


class TerminusgpsMobileAppView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Mobile Apps",
        "subtitle": "Take your tracking to-go with our mobile apps",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_mobile_app.html"
    template_name = "terminusgps/mobile_app.html"


class TerminusgpsPasswordResetView(
    HtmxTemplateResponseMixin, PasswordResetView
):
    content_type = "text/html"
    email_template_name = "terminusgps/emails/password_reset.txt"
    extra_context = {
        "title": "Password Reset",
        "subtitle": "Forgot your password?",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps/password_reset.html"
    partial_template_name = "terminusgps/partials/_password_reset.html"
    success_url = reverse_lazy("password reset done")
    subject_template_name = "terminusgps/emails/password_reset_subject.html"

    def get_form(self, form_class: forms.Form | None = None) -> forms.Form:
        """
        Adds styling to form fields.

        :param form_class: A base form class.
        :type form_class: :py:obj:`~django.forms.Form` | :py:obj:`None`
        :returns: A styled form.
        :rtype: :py:obj:`~django.forms.Form`

        """
        help_text = "Please enter the email address associated with your Terminus GPS account."
        form = super().get_form(form_class)
        form.fields["email"].label = "Email Address"
        form.fields["email"].help_text = help_text
        form.fields["email"].validators = [
            validate_email,
            validate_username_exists,
        ]
        form.fields["email"].widget.attrs.update(
            {
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "email@domain.com",
            }
        )
        return form


class TerminusgpsPasswordResetDoneView(
    HtmxTemplateResponseMixin, PasswordResetDoneView
):
    content_type = "text/html"
    extra_context = {"title": "Done Password Reset"}
    http_method_names = ["get"]
    template_name = "terminusgps/password_reset_done.html"
    partial_template_name = "terminusgps/partials/_password_reset_done.html"


class TerminusgpsPasswordResetConfirmView(
    HtmxTemplateResponseMixin, PasswordResetConfirmView
):
    content_type = "text/html"
    extra_context = {"title": "Confirm Password Reset"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps/password_reset_confirm.html"
    partial_template_name = "terminusgps/partials/_password_reset_confirm.html"
    success_url = reverse_lazy("password reset complete")

    def get_form(self, form_class: forms.Form | None = None) -> forms.Form:
        """
        Adds styling to form fields.

        :param form_class: A base form class.
        :type form_class: :py:obj:`~django.forms.Form` | :py:obj:`None`
        :returns: A styled form.
        :rtype: :py:obj:`~django.forms.Form`

        """
        form = super().get_form(form_class)
        form.fields["new_password1"].label = "New Password"
        form.fields["new_password2"].label = "Confirm New Password"
        for name in form.fields:
            form.fields[name].widget.attrs.update(
                {
                    "class": "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600"
                }
            )
        return form


class TerminusgpsPasswordResetCompleteView(
    HtmxTemplateResponseMixin, PasswordResetCompleteView
):
    content_type = "text/html"
    extra_context = {"title": "Completed Password Reset"}
    http_method_names = ["get"]
    template_name = "terminusgps/password_reset_complete.html"
    partial_template_name = (
        "terminusgps/partials/_password_reset_complete.html"
    )


class TerminusgpsLoginView(HtmxTemplateResponseMixin, LoginView):
    authentication_form = TerminusgpsAuthenticationForm
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker:dashboard")
    partial_template_name = "terminusgps/partials/_login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("tracker:dashboard")
    template_name = "terminusgps/login.html"


class TerminusgpsLogoutView(HtmxTemplateResponseMixin, LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post", "options"]
    next_page = reverse_lazy("login")
    partial_template_name = "terminusgps/partials/_logout.html"
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    template_name = "terminusgps/logout.html"


class TerminusgpsRegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
    }
    form_class = TerminusgpsRegisterForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps/register.html"
    partial_template_name = "terminusgps/partials/_register.html"
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
        )

        customer = Customer.objects.create(user=user)
        customer = self.wialon_registration_flow(form, customer)
        customer = self.authorizenet_registration_flow(form, customer)
        customer.save()
        return super().form_valid(form=form)

    @staticmethod
    @transaction.atomic
    def authorizenet_registration_flow(
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
        email_addr = str(form.cleaned_data["username"])
        customer_profile = CustomerProfile(
            email=email_addr, merchant_id=str(customer.pk)
        )
        customer.authorizenet_profile_id = customer_profile.id
        return customer

    @staticmethod
    @transaction.atomic
    def wialon_registration_flow(
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

        def calculate_account_days(start_date: datetime.date) -> int:
            return get_days_between(
                start_date,
                start_date + relativedelta(months=1, day=start_date.day),
            )

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
            resource.add_days(calculate_account_days(timezone.now()))

            customer.wialon_user_id = end_user.id
            customer.wialon_resource_id = resource.id
            return customer
