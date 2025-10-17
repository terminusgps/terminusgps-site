from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import FormView, RedirectView, TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin

from .forms import TerminusgpsRegisterForm


class TerminusgpsSourceCodeView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://github.com/terminusgps/terminusgps-site/"


class TerminusgpsHostingView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://hosting.terminusgps.com/"


class TerminusgpsNavbarView(TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_navbar.html"
    template_name = "terminusgps/navbar.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class TerminusgpsCommercialUseView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Commercial Use", "subtitle": ""}
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_commercial_use.html"
    template_name = "terminusgps/commercial_use.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class TerminusgpsIndividualUseView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Individual Use", "subtitle": ""}
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_individual_use.html"
    template_name = "terminusgps/individual_use.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class TerminusgpsAboutView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "About", "subtitle": "Why we do what we do"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_about.html"
    template_name = "terminusgps/about.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class TerminusgpsContactView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Get in touch with us"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_contact.html"
    template_name = "terminusgps/contact.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class TerminusgpsHomeView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Terminus GPS",
        "subtitle": "Industry-leading GPS monitoring hardware and software",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_home.html"
    template_name = "terminusgps/home.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class TerminusgpsTeenSafetyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Teen Safety",
        "subtitle": "Tips and Tricks for Teen Drivers",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_teen_safety.html"
    template_name = "terminusgps/teen_safety.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class TerminusgpsSeniorSafetyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Senior Safety",
        "subtitle": "Tips and Tricks for Senior Drivers",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_senior_safety.html"
    template_name = "terminusgps/senior_safety.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
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


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
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


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class TerminusgpsPrivacyPolicyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Privacy Policy",
        "subtitle": "How we use your data",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_privacy.html"
    template_name = "terminusgps/privacy.html"


@method_decorator(cache_page(timeout=60 * 15), name="get")
@method_decorator(cache_control(private=True), name="get")
class TerminusgpsRegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
    }
    form_class = TerminusgpsRegisterForm
    http_method_names = ["get", "post"]
    partial_template_name = "registration/partials/_register.html"
    success_url = reverse_lazy("dashboard")
    template_name = "registration/register.html"
