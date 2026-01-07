from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView, TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin


class SourceCodeView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://github.com/terminusgps/terminusgps-site/"


class PlatformView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://hosting.terminusgps.com/"


class IOSAppView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://apps.apple.com/us/app/terminus-gps-mobile/id1419439009"


class AndroidAppView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://play.google.com/store/apps/details?id=com.terminusgps.track&pcampaignid=web_share"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class HomeView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Home",
        "subtitle": "In God we trust, all others we track",
        "socials": [
            {
                "link": "https://www.facebook.com/TerminusGPSllc",
                "username": "TerminusGPSllc",
                "display_name": "Terminus GPS",
                "icon": "terminusgps/icon/facebook.svg",
            },
            {
                "link": "https://www.tiktok.com/@terminusgps",
                "username": "terminusgps",
                "display_name": "TerminusGps",
                "icon": "terminusgps/icon/tiktok.svg",
            },
            {
                "link": "https://nextdoor.com/pages/terminusgps-cypress-tx",
                "username": "TerminusGPS",
                "display_name": "TerminusGPS",
                "icon": "terminusgps/icon/nextdoor.svg",
            },
            {
                "link": "https://x.com/TERMINUSGPS",
                "username": "TERMINUSGPS",
                "display_name": "TERMINUSGPS",
                "icon": "terminusgps/icon/twitter.svg",
            },
        ],
    }
    http_method_names = ["get"]
    template_name = "terminusgps/home.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class AboutView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "About", "subtitle": "Why we do what we do"}
    http_method_names = ["get"]
    template_name = "terminusgps/about.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class ContactView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Get in touch with us"}
    http_method_names = ["get"]
    template_name = "terminusgps/contact.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class TermsAndConditionsView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Terms & Conditions",
        "subtitle": "You agree to these by using Terminus GPS services",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/terms.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class FrequentlyAskedQuestionsView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Frequently Asked Questions",
        "subtitle": "You have questions, we have answers",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/faq.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class PrivacyPolicyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Privacy Policy",
        "subtitle": "How we use your data",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/privacy.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class CommercialUseView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Commercial Use",
        "subtitle": "Your entire fleet, at your fingertips",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/commercial_use.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class IndividualUseView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Individual Use",
        "subtitle": "Always know where yours are",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/individual_use.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class TeenSafetyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Teen Safety",
        "subtitle": "Tips and Tricks for Teen Drivers",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/teen_safety.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class SeniorSafetyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Senior Safety",
        "subtitle": "Tips and Tricks for Senior Drivers",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/senior_safety.html"
