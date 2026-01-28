from django.views.generic import RedirectView, TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin


class SourceCodeView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://github.com/terminusgps/terminusgps-site/"


class PlatformView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    query_string = True
    url = "https://hosting.terminusgps.com/"


class IOSAppView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://apps.apple.com/us/app/terminus-gps-mobile/id1419439009"


class AndroidAppView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://play.google.com/store/apps/details?id=com.terminusgps.track&pcampaignid=web_share"


class HomeView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Home",
        "subtitle": "In God we trust, all others we track",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/home.html"


class AboutView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "About", "subtitle": "Why we do what we do"}
    http_method_names = ["get"]
    template_name = "terminusgps/about.html"


class ContactView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Get in touch with us"}
    http_method_names = ["get"]
    template_name = "terminusgps/contact.html"


class TermsAndConditionsView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Terms & Conditions",
        "subtitle": "You agree to these by using Terminus GPS services",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/terms.html"


class FrequentlyAskedQuestionsView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Frequently Asked Questions",
        "subtitle": "You have questions, we have answers",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/faq.html"


class PrivacyPolicyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Privacy Policy",
        "subtitle": "How we use your data",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/privacy.html"


class FeaturesView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Features",
        "subtitle": "Your entire fleet, at your fingertips",
    }
    http_method_names = ["get"]
    template_name = "terminusgps/features.html"
