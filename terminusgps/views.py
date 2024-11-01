from django.views.generic import RedirectView, TemplateView


class TerminusAboutView(TemplateView):
    template_name = "terminusgps/about.html"
    content_type = "text/html"
    extra_context = {"title": "About", "subtitle": "Why are we even doing this?"}
    http_method_names = ["get"]


class TerminusContactView(TemplateView):
    template_name = "terminusgps/contact.html"
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Get in touch with us"}
    http_method_names = ["get", "post"]


class TerminusPrivacyView(TemplateView):
    template_name = "terminusgps/privacy.html"
    content_type = "text/html"
    extra_context = {"title": "Privacy Policy"}
    http_method_names = ["get"]


class TerminusSourceView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://github.com/terminus-gps/terminusgps-site"
