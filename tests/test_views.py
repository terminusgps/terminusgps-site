from unittest import mock

from django.test import Client, TestCase
from django.urls import reverse

from terminusgps_site.models import ContactFormResponse


class HomeViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("home")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 200."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 200)

    def test_cache_control_header(self):
        """Fails if ``max-age=`` wasn't present in the ``Cache-Control`` response header."""
        response = self.client.get(self.location)
        self.assertStartsWith(
            response.headers.get("Cache-Control", ""), "max-age="
        )

    def test_vary_on_header(self):
        """Fails if ``HX-Request`` wasn't present in the ``Vary`` response header."""
        response = self.client.get(self.location)
        self.assertIn("HX-Request", response.headers.get("Vary", ""))

    def test_full_template_used_on_non_htmx_request(self):
        """Fails if a partial HTML template was used instead of a full page on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "terminusgps/home.html")
        headers = {"HX-Request": "false", "HX-Boosted": "true"}
        self.assertTemplateUsed(response, "terminusgps/home.html")
        headers = {"HX-Request": "false", "HX-Boosted": "false"}
        self.assertTemplateUsed(response, "terminusgps/home.html")

    def test_partial_template_used_on_htmx_request(self):
        """Fails if a full HTML response instead of a partial is rendered on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "main")


class ContactViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("contact")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 200."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 200)

    def test_cache_control_header(self):
        """Fails if ``max-age=`` wasn't present in the ``Cache-Control`` response header."""
        response = self.client.get(self.location)
        self.assertStartsWith(
            response.headers.get("Cache-Control", ""), "max-age="
        )

    def test_vary_on_header(self):
        """Fails if ``HX-Request`` wasn't present in the ``Vary`` response header."""
        response = self.client.get(self.location)
        self.assertIn("HX-Request", response.headers.get("Vary", ""))

    def test_full_template_used_on_non_htmx_request(self):
        """Fails if a partial HTML template was used instead of a full page on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "terminusgps/contact.html")
        headers = {"HX-Request": "false", "HX-Boosted": "true"}
        self.assertTemplateUsed(response, "terminusgps/contact.html")
        headers = {"HX-Request": "false", "HX-Boosted": "false"}
        self.assertTemplateUsed(response, "terminusgps/contact.html")

    def test_partial_template_used_on_htmx_request(self):
        """Fails if a full HTML response instead of a partial is rendered on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "main")

    def test_form_in_context(self):
        """Fails if an empty form wasn't added to the view context."""
        response = self.client.get(self.location)
        self.assertIn("form", response.context)


class ContactFormViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("contact form")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 200."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 200)

    def test_post_allowed(self):
        """Fails if a POST request doesn't respond with status code 200."""
        response = self.client.post(self.location)
        self.assertEqual(response.status_code, 200)

    def test_full_template_used_on_non_htmx_request(self):
        """Fails if a partial HTML template was used instead of a full page on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "terminusgps/contact_form.html")
        headers = {"HX-Request": "false", "HX-Boosted": "true"}
        self.assertTemplateUsed(response, "terminusgps/contact_form.html")
        headers = {"HX-Request": "false", "HX-Boosted": "false"}
        self.assertTemplateUsed(response, "terminusgps/contact_form.html")

    def test_partial_template_used_on_htmx_request(self):
        """Fails if a full HTML response instead of a partial is rendered on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "main")

    def test_post_with_valid_data_saves_and_redirects(self):
        """Fails if a POST request with valid data doesn't save the response and redirect the client."""
        valid_data = {
            "name": "testuser",
            "email": "testuser@domain.com",
            "message": "Test Message",
        }
        response = self.client.post(self.location, data=valid_data)
        self.assertRedirects(response, reverse("contact form success"))
        self.assertEqual(ContactFormResponse.objects.count(), 1)

    def test_post_with_valid_data_triggers_admin_email(self):
        """Fails if a POST request with valid data doesn't email the response to admins."""
        valid_data = {
            "name": "testuser",
            "email": "testuser@domain.com",
            "message": "Test Message",
        }
        with mock.patch(
            "terminusgps_site.models.ContactFormResponse.email_to_admins"
        ) as mock_email:
            self.client.post(self.location, data=valid_data)
            mock_email.assert_called_once()

    def test_post_with_invalid_data_rerenders_form_with_errors(self):
        """Fails if an invalid submission was saved or no form errors were reported."""
        invalid_data = {"name": "", "email": "", "message": ""}
        response = self.client.post(self.location, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(ContactFormResponse.objects.count(), 0)

    def test_vary_on_header(self):
        """Fails if ``HX-Request`` wasn't present in the ``Vary`` response header."""
        response = self.client.get(self.location)
        self.assertIn("HX-Request", response.headers.get("Vary", ""))


class ContactFormSuccessViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("contact form success")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 200."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 200)

    def test_cache_control_header(self):
        """Fails if ``max-age=`` wasn't present in the ``Cache-Control`` response header."""
        response = self.client.get(self.location)
        self.assertStartsWith(
            response.headers.get("Cache-Control", ""), "max-age="
        )

    def test_vary_on_header(self):
        """Fails if ``HX-Request`` wasn't present in the ``Vary`` response header."""
        response = self.client.get(self.location)
        self.assertIn("HX-Request", response.headers.get("Vary", ""))

    def test_full_template_used_on_non_htmx_request(self):
        """Fails if a partial HTML template was used instead of a full page on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(
            response, "terminusgps/contact_form_success.html"
        )
        headers = {"HX-Request": "false", "HX-Boosted": "true"}
        self.assertTemplateUsed(
            response, "terminusgps/contact_form_success.html"
        )
        headers = {"HX-Request": "false", "HX-Boosted": "false"}
        self.assertTemplateUsed(
            response, "terminusgps/contact_form_success.html"
        )

    def test_partial_template_used_on_htmx_request(self):
        """Fails if a full HTML response instead of a partial is rendered on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "main")


class AboutViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("about")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 200."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 200)

    def test_cache_control_header(self):
        """Fails if ``max-age=`` wasn't present in the ``Cache-Control`` response header."""
        response = self.client.get(self.location)
        self.assertStartsWith(
            response.headers.get("Cache-Control", ""), "max-age="
        )

    def test_vary_on_header(self):
        """Fails if ``HX-Request`` wasn't present in the ``Vary`` response header."""
        response = self.client.get(self.location)
        self.assertIn("HX-Request", response.headers.get("Vary", ""))

    def test_full_template_used_on_non_htmx_request(self):
        """Fails if a partial HTML template was used instead of a full page on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "terminusgps/about.html")
        headers = {"HX-Request": "false", "HX-Boosted": "true"}
        self.assertTemplateUsed(response, "terminusgps/about.html")
        headers = {"HX-Request": "false", "HX-Boosted": "false"}
        self.assertTemplateUsed(response, "terminusgps/about.html")

    def test_partial_template_used_on_htmx_request(self):
        """Fails if a full HTML response instead of a partial is rendered on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "main")


class TermsViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("terms")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 200."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 200)

    def test_cache_control_header(self):
        """Fails if ``max-age=`` wasn't present in the ``Cache-Control`` response header."""
        response = self.client.get(self.location)
        self.assertStartsWith(
            response.headers.get("Cache-Control", ""), "max-age="
        )

    def test_vary_on_header(self):
        """Fails if ``HX-Request`` wasn't present in the ``Vary`` response header."""
        response = self.client.get(self.location)
        self.assertIn("HX-Request", response.headers.get("Vary", ""))

    def test_full_template_used_on_non_htmx_request(self):
        """Fails if a partial HTML template was used instead of a full page on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "terminusgps/terms.html")
        headers = {"HX-Request": "false", "HX-Boosted": "true"}
        self.assertTemplateUsed(response, "terminusgps/terms.html")
        headers = {"HX-Request": "false", "HX-Boosted": "false"}
        self.assertTemplateUsed(response, "terminusgps/terms.html")

    def test_partial_template_used_on_htmx_request(self):
        """Fails if a full HTML response instead of a partial is rendered on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "main")


class PrivacyViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("privacy")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 200."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 200)

    def test_cache_control_header(self):
        """Fails if ``max-age=`` wasn't present in the ``Cache-Control`` response header."""
        response = self.client.get(self.location)
        self.assertStartsWith(
            response.headers.get("Cache-Control", ""), "max-age="
        )

    def test_vary_on_header(self):
        """Fails if ``HX-Request`` wasn't present in the ``Vary`` response header."""
        response = self.client.get(self.location)
        self.assertIn("HX-Request", response.headers.get("Vary", ""))

    def test_full_template_used_on_non_htmx_request(self):
        """Fails if a partial HTML template was used instead of a full page on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "terminusgps/privacy.html")
        headers = {"HX-Request": "false", "HX-Boosted": "true"}
        self.assertTemplateUsed(response, "terminusgps/privacy.html")
        headers = {"HX-Request": "false", "HX-Boosted": "false"}
        self.assertTemplateUsed(response, "terminusgps/privacy.html")

    def test_partial_template_used_on_htmx_request(self):
        """Fails if a full HTML response instead of a partial is rendered on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "main")


class FeaturesViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("features")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 200."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 200)

    def test_cache_control_header(self):
        """Fails if ``max-age=`` wasn't present in the ``Cache-Control`` response header."""
        response = self.client.get(self.location)
        self.assertStartsWith(
            response.headers.get("Cache-Control", ""), "max-age="
        )

    def test_vary_on_header(self):
        """Fails if ``HX-Request`` wasn't present in the ``Vary`` response header."""
        response = self.client.get(self.location)
        self.assertIn("HX-Request", response.headers.get("Vary", ""))

    def test_full_template_used_on_non_htmx_request(self):
        """Fails if a partial HTML template was used instead of a full page on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "terminusgps/features.html")
        headers = {"HX-Request": "false", "HX-Boosted": "true"}
        self.assertTemplateUsed(response, "terminusgps/features.html")
        headers = {"HX-Request": "false", "HX-Boosted": "false"}
        self.assertTemplateUsed(response, "terminusgps/features.html")

    def test_partial_template_used_on_htmx_request(self):
        """Fails if a full HTML response instead of a partial is rendered on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "main")


class FaqViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("faq")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 200."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 200)

    def test_cache_control_header(self):
        """Fails if ``max-age=`` wasn't present in the ``Cache-Control`` response header."""
        response = self.client.get(self.location)
        self.assertStartsWith(
            response.headers.get("Cache-Control", ""), "max-age="
        )

    def test_vary_on_header(self):
        """Fails if ``HX-Request`` wasn't present in the ``Vary`` response header."""
        response = self.client.get(self.location)
        self.assertIn("HX-Request", response.headers.get("Vary", ""))

    def test_full_template_used_on_non_htmx_request(self):
        """Fails if a partial HTML template was used instead of a full page on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "terminusgps/faq.html")
        headers = {"HX-Request": "false", "HX-Boosted": "true"}
        self.assertTemplateUsed(response, "terminusgps/faq.html")
        headers = {"HX-Request": "false", "HX-Boosted": "false"}
        self.assertTemplateUsed(response, "terminusgps/faq.html")

    def test_partial_template_used_on_htmx_request(self):
        """Fails if a full HTML response instead of a partial is rendered on htmx request."""
        headers = {"HX-Request": "true", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, "main")


class SourceCodeViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("source code")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 301."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 301)


class PlatformViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("platform")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 301."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 301)


class CamerasViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("cameras")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 301."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 301)


class IosAppViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("ios app")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 301."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 301)


class AndroidAppViewTestCase(TestCase):
    def setUp(self):
        self.location = reverse("android app")
        self.client = Client()

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 301."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 301)
