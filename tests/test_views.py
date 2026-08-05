from unittest import mock

import pytest
from django.test import Client, TestCase
from django.urls import reverse

from terminusgps_installer.models import InstallJob
from terminusgps_site.models import ContactFormResponse


@pytest.fixture
def client():
    return Client()


def test_home_view_get_allowed(client):
    """Fails if a GET request doesn't respond with status code 200."""
    response = client.get(reverse("home"))
    assert response.status_code == 200


def test_home_view_cache_control_header(client):
    """Fails if ``max-age=`` wasn't present in the ``Cache-Control`` response header."""
    response = client.get(reverse("home"))
    assert response.has_header("Cache-Control")
    assert response.headers["Cache-Control"].startswith("max-age=")


def test_home_view_vary_on_header(client):
    """Fails if ``HX-Request`` wasn't present in the ``Vary`` response header."""
    response = client.get(reverse("home"))
    assert response.has_header("Vary")
    assert "HX-Request" in response.headers["Vary"]


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"HX-Request": "true", "HX-Boosted": "true"},
        {"HX-Request": "false", "HX-Boosted": "true"},
    ],
)
def test_home_view_full_template_used_on_non_htmx_request(client, headers):
    """Fails if a partial HTML template was used instead of a full page on htmx request."""
    response = client.get(reverse("home"), headers=headers)
    assert response.template_name == "terminusgps/home.html"


@pytest.mark.parametrize(
    "headers",
    [{"HX-Request": "true"}, {"HX-Request": "true", "HX-Boosted": "false"}],
)
def test_home_view_partial_template_used_on_htmx_request(client, headers):
    """Fails if a full HTML response instead of a partial is rendered on htmx request."""
    response = client.get(reverse("home"), headers=headers)
    assert response.template_name == "terminusgps/home.html#main"


def test_contact_view_get_allowed(client):
    """Fails if a GET request doesn't respond with status code 200."""
    response = client.get(reverse("contact"))
    assert response.status_code == 200


def test_contact_view_cache_control_header(client):
    """Fails if ``max-age=`` wasn't present in the ``Cache-Control`` response header."""
    response = client.get(reverse("contact"))
    assert response.has_header("Cache-Control")
    assert response.headers["Cache-Control"].startswith("max-age=")


def test_contact_view_vary_on_header(client):
    """Fails if ``HX-Request`` wasn't present in the ``Vary`` response header."""
    response = client.get(reverse("contact"))
    assert response.has_header("Vary")
    assert "HX-Request" in response.headers["Vary"]


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"HX-Request": "true", "HX-Boosted": "true"},
        {"HX-Request": "false", "HX-Boosted": "true"},
    ],
)
def test_contact_view_full_template_used_on_non_htmx_request(client, headers):
    """Fails if a partial HTML template was used instead of a full page on htmx request."""
    response = client.get(reverse("contact"), headers=headers)
    assert response.template_name == "terminusgps/contact.html"


def test_contact_view_partial_template_used_on_htmx_request(client):
    """Fails if a full HTML response instead of a partial is rendered on htmx request."""
    expected_template_name = "terminusgps/contact.html#main"
    headers = {"HX-Request": "true"}
    response = client.get(reverse("contact"), headers=headers)
    assert response.template_name == expected_template_name
    headers = {"HX-Request": "true", "HX-Boosted": "false"}
    response = client.get(reverse("contact"), headers=headers)
    assert response.template_name == expected_template_name


def test_contact_view_form_in_context(client):
    """Fails if an empty form wasn't added to the view context."""
    response = client.get(reverse("contact"))
    assert "form" in response.context


def test_contact_form_view_get_allowed(client):
    """Fails if a GET request doesn't respond with status code 200."""
    response = client.get(reverse("contact form"))
    assert response.status_code == 200


def test_contact_form_view_post_allowed(client):
    """Fails if a POST request doesn't respond with status code 200."""
    response = client.post(reverse("contact form"))
    assert response.status_code == 200


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"HX-Request": "true", "HX-Boosted": "true"},
        {"HX-Request": "false", "HX-Boosted": "true"},
    ],
)
def test_contact_form_view_full_template_used_on_non_htmx_request(
    client, headers
):
    """Fails if a partial HTML template was used instead of a full page on htmx request."""
    response = client.get(reverse("contact form"), headers=headers)
    assert response.template_name == "terminusgps/contact_form.html"


def test_contact_form_view_partial_template_used_on_htmx_request(client):
    """Fails if a full HTML response instead of a partial is rendered on htmx request."""
    expected_template_name = "terminusgps/contact_form.html#main"
    headers = {"HX-Request": "true"}
    response = client.get(reverse("contact form"), headers=headers)
    assert response.template_name == expected_template_name
    headers = {"HX-Request": "true", "HX-Boosted": "false"}
    response = client.get(reverse("contact form"), headers=headers)
    assert response.template_name == expected_template_name


@pytest.mark.django_db
def test_contact_form_view_post_with_valid_data_saves_and_redirects(client):
    response = client.post(
        reverse("contact form"),
        data={
            "name": "testuser",
            "email": "testuser@domain.com",
            "message": "Test Message",
        },
    )
    assert response.status_code == 302
    assert ContactFormResponse.objects.count() == 1


@pytest.mark.django_db
def test_contact_form_view_post_with_valid_data_triggers_admin_email(client):
    with mock.patch(
        "terminusgps_site.models.ContactFormResponse.email_to_admins"
    ) as mock_email_to_admins:
        client.post(
            reverse("contact form"),
            data={
                "name": "testuser",
                "email": "testuser@domain.com",
                "message": "Test Message",
            },
        )
        mock_email_to_admins.assert_called_once()


@pytest.mark.django_db
def test_contact_form_view_post_with_invalid_data_renders_form_with_errors(
    client,
):
    response = client.post(
        reverse("contact form"), data={"name": "", "email": "", "message": ""}
    )
    assert response.status_code == 200
    assert response.context["form"].errors
    assert ContactFormResponse.objects.count() == 0


def test_contact_form_success_view_get_allowed(client):
    response = client.get(reverse("contact form success"))
    assert response.status_code == 200


def test_contact_form_success_view_cache_control_header(client):
    response = client.get(reverse("contact form success"))
    assert response.has_header("Cache-Control")
    assert response.headers["Cache-Control"].startswith("max-age=")


def test_contact_form_success_view_vary_on_header(client):
    response = client.get(reverse("contact form success"))
    assert response.has_header("Vary")
    assert "HX-Request" in response.headers["Vary"]


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"HX-Request": "true", "HX-Boosted": "true"},
        {"HX-Request": "false", "HX-Boosted": "true"},
    ],
)
def test_contact_form_success_view_full_template_used_on_non_htmx_request(
    client, headers
):
    response = client.get(reverse("contact form success"), headers=headers)
    assert response.template_name == "terminusgps/contact_form_success.html"


def test_contact_form_success_view_partial_template_used_on_htmx_request(
    client,
):
    expected_template_name = "terminusgps/contact_form_success.html#main"
    headers = {"HX-Request": "true"}
    response = client.get(reverse("contact form success"), headers=headers)
    assert response.template_name == expected_template_name
    headers = {"HX-Request": "true", "HX-Boosted": "false"}
    response = client.get(reverse("contact form success"), headers=headers)
    assert response.template_name == expected_template_name


def test_about_view_get_allowed(client):
    response = client.get(reverse("about"))
    assert response.status_code == 200


def test_about_view_cache_control_header(client):
    response = client.get(reverse("about"))
    assert response.has_header("Cache-Control")
    assert response.headers["Cache-Control"].startswith("max-age=")


def test_about_view_vary_on_header(client):
    response = client.get(reverse("about"))
    assert response.has_header("Vary")
    assert "HX-Request" in response.headers["Vary"]


def test_about_view_full_template_used_on_non_htmx_request(client):
    expected_template_name = "terminusgps/about.html"
    headers = {}
    response = client.get(reverse("about"), headers=headers)
    assert response.template_name == expected_template_name
    headers = {"HX-Request": "true", "HX-Boosted": "true"}
    response = client.get(reverse("about"), headers=headers)
    assert response.template_name == expected_template_name
    headers = {"HX-Request": "false", "HX-Boosted": "true"}
    response = client.get(reverse("about"), headers=headers)
    assert response.template_name == expected_template_name


def test_about_view_partial_template_used_on_htmx_request(client):
    expected_template_name = "terminusgps/about.html#main"
    headers = {"HX-Request": "true"}
    response = client.get(reverse("about"), headers=headers)
    assert response.template_name == expected_template_name
    headers = {"HX-Request": "true", "HX-Boosted": "false"}
    response = client.get(reverse("about"), headers=headers)
    assert response.template_name == expected_template_name


def test_terms_view_get_allowed(client):
    response = client.get(reverse("terms"))
    assert response.status_code == 200


def test_terms_view_cache_control_header(client):
    response = client.get(reverse("terms"))
    assert response.has_header("Cache-Control")
    assert response.headers["Cache-Control"].startswith("max-age=")


def test_terms_view_vary_on_header(client):
    response = client.get(reverse("terms"))
    assert "HX-Request" in response.headers.get("Vary", "")


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"HX-Request": "true", "HX-Boosted": "true"},
        {"HX-Request": "false", "HX-Boosted": "true"},
    ],
)
def test_terms_view_full_template_used_on_non_htmx_request(client, headers):
    response = client.get(reverse("terms"), headers=headers)
    assert response.template_name == "terminusgps/terms.html"


def test_terms_view_partial_template_used_on_htmx_request(client):
    expected_template_name = "terminusgps/terms.html#main"
    headers = {"HX-Request": "true"}
    response = client.get(reverse("terms"), headers=headers)
    assert response.template_name == expected_template_name
    headers = {"HX-Request": "true", "HX-Boosted": "false"}
    response = client.get(reverse("terms"), headers=headers)
    assert response.template_name == expected_template_name


def test_privacy_view_get_allowed(client):
    response = client.get(reverse("privacy"))
    assert response.status_code == 200


def test_privacy_view_cache_control_header(client):
    response = client.get(reverse("privacy"))
    assert response.has_header("Cache-Control")
    assert response.headers["Cache-Control"].startswith("max-age=")


def test_privacy_view_vary_on_header(client):
    response = client.get(reverse("privacy"))
    assert response.has_header("Vary")
    assert "HX-Request" in response.headers["Vary"]


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"HX-Request": "true", "HX-Boosted": "true"},
        {"HX-Request": "false", "HX-Boosted": "true"},
    ],
)
def test_privacy_view_full_template_used_on_non_htmx_request(client, headers):
    response = client.get(reverse("privacy"), headers=headers)
    assert response.template_name == "terminusgps/privacy.html"


def test_privacy_view_partial_template_used_on_htmx_request(client):
    expected_template_name = "terminusgps/privacy.html#main"
    headers = {"HX-Request": "true"}
    response = client.get(reverse("privacy"), headers=headers)
    assert response.template_name == expected_template_name
    headers = {"HX-Request": "true", "HX-Boosted": "false"}
    response = client.get(reverse("privacy"), headers=headers)
    assert response.template_name == expected_template_name


def test_features_view_get_allowed(client):
    response = client.get(reverse("features"))
    assert response.status_code == 200


def test_features_view_cache_control_header(client):
    response = client.get(reverse("features"))
    assert response.has_header("Cache-Control")
    assert response.headers["Cache-Control"].startswith("max-age=")


def test_features_view_vary_on_header(client):
    response = client.get(reverse("features"))
    assert response.has_header("Vary")
    assert "HX-Request" in response.headers["Vary"]


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"HX-Request": "true", "HX-Boosted": "true"},
        {"HX-Request": "false", "HX-Boosted": "true"},
    ],
)
def test_features_view_full_template_used_on_non_htmx_request(client, headers):
    response = client.get(reverse("features"), headers=headers)
    assert response.template_name == "terminusgps/features.html"


def test_features_view_partial_template_used_on_htmx_request(client):
    expected_template_name = "terminusgps/features.html#main"
    headers = {"HX-Request": "true"}
    response = client.get(reverse("features"), headers=headers)
    assert response.template_name == expected_template_name
    headers = {"HX-Request": "true", "HX-Boosted": "false"}
    response = client.get(reverse("features"), headers=headers)
    assert response.template_name == expected_template_name


def test_faq_view_get_allowed(client):
    response = client.get(reverse("faq"))
    assert response.status_code == 200


def test_faq_view_cache_control_header(client):
    response = client.get(reverse("faq"))
    assert response.has_header("Cache-Control")
    assert response.headers["Cache-Control"].startswith("max-age=")


def test_faq_view_vary_on_header(client):
    response = client.get(reverse("faq"))
    assert response.has_header("Vary")
    assert "HX-Request" in response.headers["Vary"]


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"HX-Request": "true", "HX-Boosted": "true"},
        {"HX-Request": "false", "HX-Boosted": "true"},
    ],
)
def test_faq_view_full_template_used_on_non_htmx_request(client, headers):
    response = client.get(reverse("faq"), headers=headers)
    assert response.template_name == "terminusgps/faq.html"


def test_faq_view_partial_template_used_on_htmx_request(client):
    expected_template_name = "terminusgps/faq.html#main"
    headers = {"HX-Request": "true"}
    response = client.get(reverse("faq"), headers=headers)
    assert response.template_name == expected_template_name
    headers = {"HX-Request": "true", "HX-Boosted": "false"}
    response = client.get(reverse("faq"), headers=headers)
    assert response.template_name == expected_template_name


def test_source_code_view_redirect(client):
    response = client.get(reverse("source code"))
    assert response.status_code == 301
    assert response.url == "https://github.com/terminusgps/terminusgps-site/"


def test_platform_view_redirect(client):
    response = client.get(reverse("platform"))
    assert response.status_code == 301
    assert response.url == "https://hosting.terminusgps.com/"


def test_cameras_view_redirect(client):
    response = client.get(reverse("cameras"))
    assert response.status_code == 301
    assert response.url == "https://camera.terminusgps.com/"


def test_ios_app_view_redirect(client):
    response = client.get(reverse("ios app"))
    assert response.status_code == 301
    assert (
        response.url
        == "https://apps.apple.com/us/app/terminus-gps-mobile/id1419439009"
    )


def test_android_app_view_redirect(client):
    response = client.get(reverse("android app"))
    assert response.status_code == 301
    assert (
        response.url
        == "https://play.google.com/store/apps/details?id=com.terminusgps.track&pcampaignid=web_share"
    )


class InstallerHomeViewTestCase(TestCase):
    fixtures = ["terminusgps/fixtures/terminusgps/tests/test_users.json"]

    def setUp(self):
        self.location = reverse("installer:home")
        self.client = Client()
        self.client.login(**{"username": "testuser", "password": "trolldad"})

    def tearDown(self):
        self.client.logout()

    def test_anonymous_get_forbidden(self):
        """Fails if a GET request from an anonymous user doesn't respond with status code 302 (redirect to login)."""
        self.client.logout()
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 302)

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
        expected_template_name = "installer/home.html"
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, expected_template_name)
        headers = {"HX-Request": "false", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, expected_template_name)
        headers = {"HX-Request": "false", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, expected_template_name)

    def test_partial_template_used_on_htmx_request(self):
        """Fails if a full HTML response instead of a partial is rendered on htmx request."""
        expected_template_name = "main"
        headers = {"HX-Request": "true", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, expected_template_name)


class InstallerNewJobFormViewTestCase(TestCase):
    fixtures = [
        "terminusgps/fixtures/terminusgps/tests/test_employees.json",
        "terminusgps/fixtures/terminusgps/tests/test_users.json",
        "terminusgps/fixtures/terminusgps/tests/test_wialonresources.json",
    ]

    def setUp(self):
        self.location = reverse("installer:new job form")
        self.client = Client()
        self.client.login(**{"username": "testuser", "password": "trolldad"})

    def tearDown(self):
        self.client.logout()

    def test_anonymous_get_forbidden(self):
        """Fails if a GET request from an anonymous user doesn't respond with status code 302 (redirect to login)."""
        self.client.logout()
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 302)

    def test_anonymous_post_forbidden(self):
        """Fails if a POST request from an anonymous user doesn't respond with status code 302 (redirect to login)."""
        self.client.logout()
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 302)

    def test_get_allowed(self):
        """Fails if a GET request doesn't respond with status code 200."""
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 200)


class InstallJobListViewTestCase(TestCase):
    fixtures = [
        "terminusgps/fixtures/terminusgps/tests/test_users.json",
        "terminusgps/fixtures/terminusgps/tests/test_employees.json",
        "terminusgps/fixtures/terminusgps/tests/test_installjobs.json",
        "terminusgps/fixtures/terminusgps/tests/test_wialonresources.json",
        "terminusgps/fixtures/terminusgps/tests/test_wialonunits.json",
    ]

    def setUp(self):
        self.location = reverse("installer:job list")
        self.client = Client()
        self.client.login(**{"username": "testuser", "password": "trolldad"})

    def tearDown(self):
        self.client.logout()

    def test_anonymous_get_forbidden(self):
        """Fails if a GET request from an anonymous user doesn't respond with status code 302 (redirect to login)."""
        self.client.logout()
        response = self.client.get(self.location)
        self.assertEqual(response.status_code, 302)

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
        expected_template_name = "installer/job_list.html"
        headers = {"HX-Request": "true", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, expected_template_name)
        headers = {"HX-Request": "false", "HX-Boosted": "true"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, expected_template_name)
        headers = {"HX-Request": "false", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, expected_template_name)

    def test_partial_template_used_on_htmx_request(self):
        """Fails if a full HTML response instead of a partial is rendered on htmx request."""
        expected_template_name = "main"
        headers = {"HX-Request": "true", "HX-Boosted": "false"}
        response = self.client.get(self.location, headers=headers)
        self.assertTemplateUsed(response, expected_template_name)

    def test_jobs_list_in_context(self):
        """Fails if ``jobs_list`` wasn't present in the view context."""
        response = self.client.get(self.location)
        self.assertIn("jobs_list", response.context)

    def test_only_not_done_jobs_in_context(self):
        """Fails if a job with status ``done`` was present in the view context."""
        expected_qs = InstallJob.objects.exclude(status="done")
        response = self.client.get(self.location)
        result_qs = response.context.get("jobs_list")
        self.assertIsNotNone(result_qs)
        self.assertQuerySetEqual(expected_qs, result_qs)
