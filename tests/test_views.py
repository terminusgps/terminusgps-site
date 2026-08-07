from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from terminusgps_site.models import ContactFormResponse


@pytest.fixture
def client():
    return Client()


def test_login_view_get_allowed(client):
    """Fails if a GET request doesn't respond with status code 200."""
    response = client.get(reverse("login"))
    assert response.status_code == 200


def test_login_view_post_allowed(client):
    """Fails if a POST request doesn't respond with status code 200."""
    response = client.post(reverse("login"))
    assert response.status_code == 200


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
    response = client.get(reverse("home"), headers=headers)
    assert response.template_name == "terminusgps/home.html"


@pytest.mark.parametrize(
    "headers",
    [{"HX-Request": "true"}, {"HX-Request": "true", "HX-Boosted": "false"}],
)
def test_home_view_partial_template_used_on_htmx_request(client, headers):
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
    response = client.get(reverse("contact"), headers=headers)
    assert response.template_name == "terminusgps/contact.html"


@pytest.mark.parametrize(
    "headers",
    [{"HX-Request": "true"}, {"HX-Request": "true", "HX-Boosted": "false"}],
)
def test_contact_view_partial_template_used_on_htmx_request(client, headers):
    response = client.get(reverse("contact"), headers=headers)
    assert response.template_name == "terminusgps/contact.html#main"


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


@pytest.mark.parametrize(
    "headers",
    [{"HX-Request": "true"}, {"HX-Request": "true", "HX-Boosted": "false"}],
)
def test_contact_form_view_partial_template_used_on_htmx_request(
    client, headers
):
    """Fails if a full HTML response instead of a partial is rendered on htmx request."""
    response = client.get(reverse("contact form"), headers=headers)
    assert response.template_name == "terminusgps/contact_form.html#main"


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


@pytest.mark.parametrize(
    "headers",
    [{"HX-Request": "true"}, {"HX-Request": "true", "HX-Boosted": "false"}],
)
def test_contact_form_success_view_partial_template_used_on_htmx_request(
    client, headers
):
    response = client.get(reverse("contact form success"), headers=headers)
    assert (
        response.template_name == "terminusgps/contact_form_success.html#main"
    )


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


@pytest.mark.parametrize(
    "headers",
    [{"HX-Request": "true"}, {"HX-Request": "true", "HX-Boosted": "false"}],
)
def test_about_view_partial_template_used_on_htmx_request(client, headers):
    response = client.get(reverse("about"), headers=headers)
    assert response.template_name == "terminusgps/about.html#main"


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


@pytest.mark.parametrize(
    "headers",
    [{"HX-Request": "true"}, {"HX-Request": "true", "HX-Boosted": "false"}],
)
def test_terms_view_partial_template_used_on_htmx_request(client, headers):
    response = client.get(reverse("terms"), headers=headers)
    assert response.template_name == "terminusgps/terms.html#main"


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


@pytest.mark.parametrize(
    "headers",
    [{"HX-Request": "true"}, {"HX-Request": "true", "HX-Boosted": "false"}],
)
def test_privacy_view_partial_template_used_on_htmx_request(client, headers):
    response = client.get(reverse("privacy"), headers=headers)
    assert response.template_name == "terminusgps/privacy.html#main"


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


@pytest.mark.parametrize(
    "headers",
    [{"HX-Request": "true"}, {"HX-Request": "true", "HX-Boosted": "false"}],
)
def test_features_view_partial_template_used_on_htmx_request(client, headers):
    response = client.get(reverse("features"), headers=headers)
    assert response.template_name == "terminusgps/features.html#main"


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


@pytest.mark.parametrize(
    "headers",
    [{"HX-Request": "true"}, {"HX-Request": "true", "HX-Boosted": "false"}],
)
def test_faq_view_partial_template_used_on_htmx_request(client, headers):
    response = client.get(reverse("faq"), headers=headers)
    assert response.template_name == "terminusgps/faq.html#main"


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


def test_installer_home_view_anonymous_get_forbidden(client):
    response = client.get(reverse("installer:home"))
    assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_installer_home_view_get_allowed(client):
    username = "testuser"
    password = "super_secure_password1!"
    get_user_model().objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    response = client.get(reverse("installer:home"))
    assert response.status_code == 200
