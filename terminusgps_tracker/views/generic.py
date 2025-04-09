from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import RedirectView, TemplateView

from terminusgps_tracker.views.mixins import (
    HtmxTemplateResponseMixin,
    TrackerAppConfigContextMixin,
)

if not hasattr(settings, "TRACKER_APP_CONFIG"):
    raise ImproperlyConfigured("'TRACKER_APP_CONFIG' setting is required.")


class TrackerSourceCodeView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_APP_CONFIG.get("REPOSITORY_URL")


class TrackerHostingView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://hosting.terminusgps.com/"


class TrackerPrivacyPolicyView(
    TrackerAppConfigContextMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_privacy.html"
    template_name = "terminusgps_tracker/privacy.html"
    extra_context = {
        "title": "Privacy Policy",
        "subtitle": "How we use your data",
        "class": "flex flex-col gap-4",
    }


class TrackerMobileAppView(
    TrackerAppConfigContextMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Mobile Apps",
        "subtitle": "Take your tracking to-go with our mobile apps",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_mobile_app.html"
    template_name = "terminusgps_tracker/mobile_app.html"
