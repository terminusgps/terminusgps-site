import logging
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from terminusgps_installer.models import Employee, WialonResource, WialonUnit

logging.disable(logging.CRITICAL)


@pytest.fixture(autouse=True)
def mock_api():
    with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
        mock_api = MagicMock()
        mock_api.token_login.return_value = {
            "eid": "abc123",
            "au": "test",
            "user": {"id": 1},
            "gis_sid": "def456",
        }
        mock_api.core_search_items.return_value = {
            "totalItemsCount": 1,
            "items": [{"id": 1, "nm": "Unit #1"}],
        }
        mock_wialon_cls.return_value = mock_api
        yield mock_api


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def credentials():
    return {"username": "testuser", "password": "super_secure_password1!"}


@pytest.fixture(autouse=True)
def user(credentials):
    return get_user_model().objects.create_user(**credentials)


@pytest.fixture(autouse=True)
def employee(user):
    return Employee.objects.create(user=user)


@pytest.fixture(autouse=True)
def resource():
    return WialonResource.objects.create(pk=1, name="Resource #1")


@pytest.mark.e2e
@pytest.mark.django_db
def test_new_job_form_one_unit_redirects_and_saves(live_server, credentials):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{live_server.url}{reverse('login')}")
        page.get_by_label("Username").fill(credentials["username"])
        page.get_by_label("Password").fill(credentials["password"])
        page.get_by_role("button", name="Login").click()
        page.goto(f"{live_server.url}{reverse('installer:new job form')}")
        page.get_by_label("Company").select_option("Resource #1")
        page.get_by_label("Employee").select_option("testuser")
        page.get_by_label("Imei").fill("12345678912345678")
        page.get_by_label("Vin").fill("12345678912345678")
        page.get_by_label("Plate").fill("ABC1234")
        page.get_by_role("button", name="Submit").click()
        browser.close()


@pytest.mark.e2e
@pytest.mark.django_db
def test_new_job_form_non_digit_imei_adds_error(live_server, credentials):
    expected_error_message = "This value cannot contain non-digits, got 'abc'."
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{live_server.url}{reverse('login')}")
        page.get_by_label("Username").fill(credentials["username"])
        page.get_by_label("Password").fill(credentials["password"])
        page.get_by_role("button", name="Login").click()
        page.goto(f"{live_server.url}{reverse('installer:new job form')}")
        page.get_by_label("Company").select_option("Resource #1")
        page.get_by_label("Employee").select_option("testuser")
        page.get_by_label("Imei").fill("abc")
        page.get_by_role("button", name="Submit").click()
        expect(page.get_by_text(expected_error_message)).to_have_count(1)
        browser.close()


@pytest.mark.e2e
@pytest.mark.django_db
def test_new_job_form_two_units_redirects_and_saves(live_server, credentials):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{live_server.url}{reverse('login')}")
        page.get_by_label("Username").fill(credentials["username"])
        page.get_by_label("Password").fill(credentials["password"])
        page.get_by_role("button", name="Login").click()
        page.goto(f"{live_server.url}{reverse('installer:new job form')}")
        page.get_by_label("Company").select_option("Resource #1")
        page.get_by_label("Employee").select_option("testuser")
        page.get_by_label("Imei:").fill("12345678912345678")
        page.get_by_label("Vin:").fill("12345678912345678")
        page.get_by_label("Plate:").fill("ABC1234")
        page.get_by_role("button", name="Add Unit").click()
        page.get_by_label("Imei:").nth(1).fill("98765432198765432")
        page.get_by_label("Vin:").nth(1).fill("98765432198765432")
        page.get_by_label("Plate:").nth(1).fill("ABC1234")
        page.get_by_role("button", name="Submit").click()
        browser.close()
    assert WialonUnit.objects.count() == 2
    assert WialonUnit.objects.get(imei="12345678912345678")
    assert WialonUnit.objects.get(imei="98765432198765432")
