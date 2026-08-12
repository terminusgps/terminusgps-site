import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from terminusgps_installer.models import (
    Employee,
    InstallJob,
    WialonResource,
    WialonUnit,
)


@pytest.fixture(scope="module")
def user(django_db_blocker, credentials):
    with django_db_blocker.unblock():
        user = get_user_model().objects.create_user(**credentials)
    yield user
    with django_db_blocker.unblock():
        user.delete()


@pytest.fixture(scope="module")
def employee(django_db_blocker, user):
    with django_db_blocker.unblock():
        employee = Employee.objects.create(user=user)
    yield employee
    with django_db_blocker.unblock():
        employee.delete()


@pytest.fixture(scope="module")
def resource(django_db_blocker):
    with django_db_blocker.unblock():
        resource = WialonResource.objects.create(pk=1, name="Resource #1")
    yield resource
    with django_db_blocker.unblock():
        resource.delete()


@pytest.fixture(scope="module")
def installjob(django_db_blocker, employee, resource):
    with django_db_blocker.unblock():
        installjob = InstallJob.objects.create(
            employee=employee, company=resource
        )
    yield installjob
    with django_db_blocker.unblock():
        installjob.delete()


@pytest.fixture(scope="module")
def units(django_db_blocker, installjob):
    with django_db_blocker.unblock():
        unit_1 = WialonUnit.objects.create(
            job=installjob, name="Unit #1", imei="abc123"
        )
        unit_2 = WialonUnit.objects.create(
            job=installjob, name="Unit #2", imei="def456"
        )
    yield WialonUnit.objects.filter(job=installjob)
    with django_db_blocker.unblock():
        unit_1.delete()
        unit_2.delete()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "location,expected_template_name",
    [
        (reverse("home"), "terminusgps/home.html"),
        (reverse("about"), "terminusgps/about.html"),
        (reverse("terms"), "terminusgps/terms.html"),
        (reverse("privacy"), "terminusgps/privacy.html"),
        (reverse("contact"), "terminusgps/contact.html"),
        (reverse("features"), "terminusgps/features.html"),
        (reverse("faq"), "terminusgps/faq.html"),
        (reverse("contact form"), "terminusgps/contact_form.html"),
        (
            reverse("contact form success"),
            "terminusgps/contact_form_success.html",
        ),
        (reverse("installer:job list"), "installer/job_list.html"),
    ],
)
def test_full_template_rendered_on_non_htmx_request(
    client,
    credentials,
    user,
    employee,
    resource,
    installjob,
    units,
    location,
    expected_template_name,
):
    client.login(**credentials)
    headers = {}
    response = client.get(location, headers=headers)
    assert response.template_name == expected_template_name


@pytest.mark.django_db
@pytest.mark.parametrize(
    "location,expected_template_name",
    [
        (reverse("home"), "terminusgps/home.html"),
        (reverse("about"), "terminusgps/about.html"),
        (reverse("terms"), "terminusgps/terms.html"),
        (reverse("privacy"), "terminusgps/privacy.html"),
        (reverse("contact"), "terminusgps/contact.html"),
        (reverse("features"), "terminusgps/features.html"),
        (reverse("faq"), "terminusgps/faq.html"),
        (reverse("contact form"), "terminusgps/contact_form.html"),
        (
            reverse("contact form success"),
            "terminusgps/contact_form_success.html",
        ),
    ],
)
def test_full_template_rendered_on_boosted_htmx_request(
    client, location, expected_template_name
):
    headers = {"HX-Request": "true", "HX-Boosted": "true"}
    response = client.get(location, headers=headers)
    assert response.template_name == expected_template_name


@pytest.mark.django_db
@pytest.mark.parametrize(
    "location,expected_template_name",
    [
        (reverse("home"), "terminusgps/home.html#main"),
        (reverse("about"), "terminusgps/about.html#main"),
        (reverse("terms"), "terminusgps/terms.html#main"),
        (reverse("privacy"), "terminusgps/privacy.html#main"),
        (reverse("contact"), "terminusgps/contact.html#main"),
        (reverse("features"), "terminusgps/features.html#main"),
        (reverse("faq"), "terminusgps/faq.html#main"),
        (reverse("contact form"), "terminusgps/contact_form.html#main"),
        (
            reverse("contact form success"),
            "terminusgps/contact_form_success.html#main",
        ),
    ],
)
def test_partial_template_rendered_on_htmx_request(
    client, location, expected_template_name
):
    headers = {"HX-Request": "true"}
    response = client.get(location, headers=headers)
    assert response.template_name == expected_template_name


@pytest.mark.django_db
@pytest.mark.parametrize(
    "location",
    [
        reverse("home"),
        reverse("about"),
        reverse("terms"),
        reverse("privacy"),
        reverse("contact"),
        reverse("features"),
        reverse("faq"),
        reverse("contact form"),
        reverse("contact form success"),
    ],
)
def test_get_allowed(client, location):
    response = client.get(location)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "location",
    [
        reverse("home"),
        reverse("about"),
        reverse("terms"),
        reverse("privacy"),
        reverse("contact"),
        reverse("features"),
        reverse("faq"),
        reverse("contact form"),
        reverse("contact form success"),
    ],
)
def test_vary_header(client, location):
    response = client.get(location)
    assert response.has_header("Vary")
    assert "HX-Request" in response.headers["Vary"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "location",
    [
        reverse("home"),
        reverse("about"),
        reverse("terms"),
        reverse("privacy"),
        reverse("contact"),
        reverse("features"),
        reverse("faq"),
        reverse("contact form"),
        reverse("contact form success"),
    ],
)
def test_cache_control_header(client, location):
    response = client.get(location)
    assert response.has_header("Cache-Control")
    assert response.headers["Cache-Control"].startswith("max-age=")


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
