from django.test import RequestFactory, TestCase

from manager.views import request_is_htmx


class RequestIsHtmxTestCase(TestCase):
    def test_non_boosted_htmx_request(self):
        """Fails if a non-boosted htmx request returns :py:obj:`False`."""
        factory = RequestFactory()
        headers = {"HX-Request": "true"}
        request = factory.get("/", headers=headers)
        result = request_is_htmx(request)
        self.assertTrue(result)

    def test_boosted_htmx_request(self):
        """Fails if a boosted htmx request returns :py:obj:`True`."""
        factory = RequestFactory()
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        request = factory.get("/", headers=headers)
        result = request_is_htmx(request)
        self.assertFalse(result)

    def test_non_htmx_request(self):
        """Fails if a non-htmx request returns :py:obj:`True`."""
        factory = RequestFactory()
        headers = {}
        request = factory.get("/", headers=headers)
        result = request_is_htmx(request)
        self.assertFalse(result)
