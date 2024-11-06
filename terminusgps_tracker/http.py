from django.http import HttpRequest as HttpRequestBase
from django.http import HttpResponse as HttpResponseBase
from django_htmx.middleware import HtmxDetails


class HttpRequest(HttpRequestBase):
    htmx: HtmxDetails


class HttpResponse(HttpResponseBase):
    """Original"""
