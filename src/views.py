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
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, RedirectView, TemplateView
from terminusgps.authorizenet.profiles import CustomerProfile
from terminusgps.authorizenet.utils import get_days_between
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import constants
from terminusgps.wialon.items import WialonResource, WialonUser
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.models import Customer

from .forms import (
    TerminusgpsAuthenticationForm,
    TerminusgpsEmailSupportForm,
    TerminusgpsRegisterForm,
)
from .validators import validate_username_exists

if settings.configured and not hasattr(settings, "TRACKER_APP_CONFIG"):
    raise ImproperlyConfigured("'TRACKER_APP_CONFIG' setting is required.")


class TerminusgpsSourceCodeView(RedirectView):
    """
    Redirects the client to the application's source code repository.

    **HTTP Methods**:
        - GET

    """

    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_APP_CONFIG.get("REPOSITORY_URL")


class TerminusgpsHostingView(RedirectView):
    """
    Redirects the client to the the Terminus GPS hosting site.

    **HTTP Methods**:
        - GET

    """

    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_APP_CONFIG.get("HOSTING_URL")


class TerminusgpsPrivacyPolicyView(HtmxTemplateResponseMixin, TemplateView):
    """
    Renders the privacy policy for the application.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"Privacy Policy"``

    ``class``
        The `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    ``subtitle``
        The subtitle for the view/webpage.

        Value: ``"How we use your data"``

    **HTTP Methods:**
        - GET

    **Template:**
        :template:`terminusgps/privacy.html`

    **Partial Template:**
        :template:`terminusgps/partials/_privacy.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite
    """

    content_type = "text/html"
    extra_context = {
        "title": "Privacy Policy",
        "subtitle": "How we use your data",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_privacy.html"
    template_name = "terminusgps/privacy.html"


class TerminusgpsMobileAppView(HtmxTemplateResponseMixin, TemplateView):
    """
    Renders links to mobile app download pages for the application.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"Mobile Apps"``

    ``class``
        The `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    ``subtitle``
        The subtitle for the view/webpage.

        Value: ``"Take your tracking to-go with our mobile apps"``

    **HTTP Methods:**
        - GET

    **Template:**
        :template:`terminusgps/mobile_app.html`

    **Partial Template:**
        :template:`terminusgps/partials/_mobile_app.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    extra_context = {
        "title": "Mobile Apps",
        "subtitle": "Take your tracking to-go with our mobile apps",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_mobile_app.html"
    template_name = "terminusgps/mobile_app.html"


class TerminusgpsSupportView(HtmxTemplateResponseMixin, TemplateView):
    """
    Renders the support options for the application.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"Support"``

    ``class``
        The `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    ``subtitle``
        The subtitle for the view/webpage.

        Value: ``"Drop us a line"``

    **HTTP Methods:**
        - GET

    **Template:**
        :template:`terminusgps/support.html`

    **Partial Template:**
        :template:`terminusgps/partials/_support.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    extra_context = {
        "title": "Support",
        "subtitle": "Drop us a line",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/support.html"
    partial_template_name = "terminusgps/partials/_support.html"


class TerminusgpsSupportCallView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Call Support",
        "subtitle": "Give us a ring and we'll get back to you asap",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/support_call.html"
    partial_template_name = "terminusgps/partials/_support_call.html"


class TerminusgpsSupportEmailView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Email Support",
        "subtitle": "Shoot us an email and we'll get back to you asap",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps/support_email.html"
    partial_template_name = "terminusgps/partials/_support_email.html"
    form_class = TerminusgpsEmailSupportForm

    def form_valid(
        self, form: TerminusgpsEmailSupportForm
    ) -> HttpResponse | HttpResponseRedirect:
        email = EmailMessage(
            subject=form.cleaned_data["subject"],
            body=form.cleaned_data["message"],
            to=["support@terminusgps.com"],
            cc=["blake@terminusgps.com"],
            reply_to=[form.cleaned_data["email"]],
        )
        email.send(fail_silently=True)
        return super().form_valid(form=form)


class TerminusgpsSupportChatView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Chat Support",
        "subtitle": "Send us a message and we'll get back to you asap",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps/support_chat.html"
    partial_template_name = "terminusgps/partials/_support_chat.html"


class TerminusgpsPasswordResetView(HtmxTemplateResponseMixin, PasswordResetView):
    """
    Renders a password reset form and sends a password reset email.

    **Context**

    ``class``
        The `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    ``form``
        A form that takes an email address for a password reset.

    ``title``
        The title for the view/webpage.

        Value: ``"Password Reset"``

    ``subtitle``
        The subtitle for the view/webpage.

        Value: ``"Forgot your password?"``

    **HTTP Methods:**
        - GET
        - POST

    **Template:**
        :template:`terminusgps/password_reset.html`

    **Partial Template:**
        :template:`terminusgps/partials/_password_reset.html`

    **Email Template:**
        :template:`terminusgps/emails/password_reset.txt`

    **Subject Template:**
        :template:`terminusgps/emails/password_reset_subject.txt`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    email_template_name = "terminusgps/emails/password_reset.txt"
    extra_context = {
        "title": "Password Reset",
        "subtitle": "Forgot your password?",
        "class": "flex flex-col gap-4",
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
        help_text = (
            "Please enter the email address associated with your Terminus GPS account."
        )
        form = super().get_form(form_class)
        form.fields["email"].label = "Email Address"
        form.fields["email"].help_text = help_text
        form.fields["email"].validators = [validate_email, validate_username_exists]
        form.fields["email"].widget.attrs.update(
            {
                "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                "placeholder": "email@domain.com",
            }
        )
        return form


class TerminusgpsPasswordResetDoneView(
    HtmxTemplateResponseMixin, PasswordResetDoneView
):
    """
    Renders a confirmation that a password reset email was sent successfully.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"Done Password Reset"``

    **HTTP Methods:**
        - GET

    **Template:**
        :template:`terminusgps/password_reset_done.html`

    **Partial Template:**
        :template:`terminusgps/partials/_password_reset_done.html`

    """

    content_type = "text/html"
    extra_context = {"title": "Done Password Reset"}
    http_method_names = ["get"]
    template_name = "terminusgps/password_reset_done.html"
    partial_template_name = "terminusgps/partials/_password_reset_done.html"


class TerminusgpsPasswordResetConfirmView(
    HtmxTemplateResponseMixin, PasswordResetConfirmView
):
    """
    Renders a form to update a password to a new password.

    **Context**

    ``form``
        A password reset form.

    ``class``
        The `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    ``title``
        The title for the view/webpage.

        Value: ``"Confirm Password Reset"``

    **HTTP Methods:**
        - GET
        - POST

    **Template:**
        :template:`terminusgps/password_reset_confirm.html`

    **Partial Template:**
        :template:`terminusgps/partials/_password_reset_confirm.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    extra_context = {"title": "Confirm Password Reset", "class": "flex flex-col gap-4"}
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
    """
    Rendered after a password reset was completed successfully.

    **Context**

    ``class``
        The `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    ``title``
        The title for the view/webpage.

        Value: ``"Completed Password Reset"``

    **HTTP Methods:**
        - GET

    **Template:**
        :template:`terminusgps/password_reset_complete.html`

    **Partial Template:**
        :template:`terminusgps/partials/_password_reset_complete.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    extra_context = {"title": "Completed Password Reset"}
    http_method_names = ["get"]
    template_name = "terminusgps/password_reset_complete.html"
    partial_template_name = "terminusgps/partials/_password_reset_complete.html"


class TerminusgpsLoginView(HtmxTemplateResponseMixin, LoginView):
    """
    Renders a login form and logs a user in.

    **Context**

    ``class``
        The `tailwindcss`_ class used for the view.

        Value: ``"p-4 flex flex-col gap-2"``

    ``title``
        The title for the view/webpage.

        Value: ``"Login"``

    ``subtitle``
        The subtitle for the view/webpage.

        Value: ``"We know where ours are... do you?"``

    **HTTP Methods:**
        - GET
        - POST

    **Template:**
        :template:`terminusgps/login.html`

    **Partial Template:**
        :template:`terminusgps/partials/_login.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    authentication_form = TerminusgpsAuthenticationForm
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
        "class": "p-4 flex flex-col gap-2",
    }
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker:dashboard")
    partial_template_name = "terminusgps/partials/_login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("tracker:dashboard")
    template_name = "terminusgps/login.html"


class TerminusgpsLogoutView(HtmxTemplateResponseMixin, LogoutView):
    """
    Renders a logout button and logs a user out.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"Logout"``

    **HTTP Methods:**
        - GET
        - POST
        - OPTIONS

    **Template:**
        :template:`terminusgps/logout.html`

    **Partial Template:**
        :template:`terminusgps/partials/_logout.html`

    """

    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post", "options"]
    next_page = reverse_lazy("login")
    partial_template_name = "terminusgps/partials/_logout.html"
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    template_name = "terminusgps/logout.html"


class TerminusgpsRegisterView(HtmxTemplateResponseMixin, FormView):
    """
    Registers a new user and redirects the client to the tracker dashboard.

    **Context**

    ``class``
        The `tailwindcss`_ class used for the view.

        Value: ``"p-4 flex flex-col gap-4"``

    ``title``
        The title for the view/webpage.

        Value: ``"Register"``

    ``subtitle``
        The subtitle for the view/webpage.

        Value: ``"You'll know where yours are..."``

    **HTTP Methods:**
        - GET
        - POST

    **Template:**
        :template:`terminusgps/register.html`

    **Partial Template:**
        :template:`terminusgps/partials/_register.html`

    """

    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
        "class": "p-4 flex flex-col gap-4",
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
        return HttpResponseRedirect(self.get_success_url())

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
        customer.authorizenet_id = customer_profile.id
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
                start_date, start_date + relativedelta(months=1, day=start_date.day)
            )

        username: str = form.cleaned_data["username"]
        password: str = form.cleaned_data["password1"]

        with WialonSession() as session:
            super_user = WialonUser(
                id=None,
                session=session,
                creator_id=settings.WIALON_ADMIN_ID,
                name=f"super_{username}",  # super_email@domain.com
                password=password,
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
