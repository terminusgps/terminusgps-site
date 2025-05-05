from django.conf import settings
from django.views.generic import RedirectView, TemplateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.views.mixins import TrackerAppConfigContextMixin


class TrackerSourceCodeView(TrackerAppConfigContextMixin, RedirectView):
    """
    Redirects the client to the application's source code repository.

    **HTTP Methods**:
        - GET

    """

    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_APP_CONFIG.get("REPOSITORY_URL")


class TrackerHostingView(TrackerAppConfigContextMixin, RedirectView):
    """
    Redirects the client to the the Terminus GPS hosting site.

    **HTTP Methods**:
        - GET

    """

    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_APP_CONFIG.get("HOSTING_URL")


class TrackerPrivacyPolicyView(
    TrackerAppConfigContextMixin, HtmxTemplateResponseMixin, TemplateView
):
    """
    Renders the privacy policy for the application.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"Privacy Policy"``

    ``subtitle``
        The subtitle for the view/webpage.

        Value: ``"How we use your data"``

    ``class``
        A `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    **HTTP Methods:**
        - GET

    **Template:**
        :template:`terminusgps_tracker/privacy.html`

    **Partial Template:**
        :template:`terminusgps_tracker/partials/_privacy.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    extra_context = {
        "title": "Privacy Policy",
        "subtitle": "How we use your data",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_privacy.html"
    template_name = "terminusgps_tracker/privacy.html"


class TrackerMobileAppView(
    TrackerAppConfigContextMixin, HtmxTemplateResponseMixin, TemplateView
):
    """
    Renders the mobile app download buttons for the application.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"Mobile Apps"``

    ``subtitle``
        The subtitle for the view/webpage.

        Value: ``"Take your tracking to-go with our mobile apps."``

    ``class``
        A `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    **HTTP Methods:**
        - GET

    **Template:**
        :template:`terminusgps_tracker/mobile_app.html`

    **Partial Template:**
        :template:`terminusgps_tracker/partials/_mobile_app.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    extra_context = {
        "title": "Mobile Apps",
        "subtitle": "Take your tracking to-go with our mobile apps",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_mobile_app.html"
    template_name = "terminusgps_tracker/mobile_app.html"
