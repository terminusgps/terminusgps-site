from django.views.generic import TemplateView, RedirectView
from django.conf import settings

from terminusgps_tracker.http import HttpRequest, HttpResponse


class TrackerValidationView(TemplateView):
    template_name = "terminusgps_tracker/forms/field.html"
    content_type = "text/html"
    http_method_names = ["post"]

    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        if not request.htmx:
            return HttpResponse(status=401)
        return self.render_to_response(context=self.get_context_data(), **kwargs)


class TrackerSubscriptionView(TemplateView):
    template_name = "terminusgps_tracker/subscriptions.html"
    content_type = "text/html"
    extra_context = {"title": "Subscriptions", "subtitle": "Our subscription options"}
    http_method_names = ["get"]


class TrackerAboutView(TemplateView):
    template_name = "terminusgps_tracker/about.html"
    content_type = "text/html"
    extra_context = {"title": "About", "subtitle": "Why are we even doing this?"}
    http_method_names = ["get"]


class TrackerContactView(TemplateView):
    template_name = "terminusgps_tracker/contact.html"
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Get in touch with us"}
    http_method_names = ["get", "post"]


class TrackerPrivacyView(TemplateView):
    template_name = "terminusgps_tracker/privacy.html"
    content_type = "text/html"
    extra_context = {"title": "Privacy Policy"}
    http_method_names = ["get"]


class TrackerSourceView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_SOURCE_URL
