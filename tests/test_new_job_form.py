import logging

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from terminusgps_installer.models import (
    Employee,
    InstallJob,
    WialonResource,
    WialonUnit,
)

logging.disable(logging.CRITICAL)


@pytest.fixture(autouse=True)
def user(credentials):
    yield get_user_model().objects.create_user(**credentials)


@pytest.fixture(autouse=True)
def employee(user):
    yield Employee.objects.create(user=user)


@pytest.fixture(autouse=True)
def resource():
    yield WialonResource.objects.create(pk=1, name="Resource #1")


@pytest.mark.e2e
@pytest.mark.django_db
def test_new_job_form_one_unit_redirects_and_saves(
    live_server, credentials, mock_api
):
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 1,
        "items": [{"id": 1, "nm": "Unit #1"}],
    }
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
        expect(page).to_have_title("In-Progress Jobs | Terminus GPS")
        browser.close()
    assert InstallJob.objects.count() == 1
    assert WialonUnit.objects.get(imei="12345678912345678")


@pytest.mark.e2e
@pytest.mark.django_db
def test_new_job_form_non_digit_imei_adds_error(
    live_server, credentials, mock_api
):
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 1,
        "items": [{"id": 1, "nm": "Unit #1"}],
    }
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
        expect(page).to_have_title("New Install Job | Terminus GPS")
        expect(page.get_by_text(expected_error_message)).to_have_count(1)
        browser.close()
    assert InstallJob.objects.count() == 0


@pytest.mark.e2e
@pytest.mark.django_db
def test_new_job_form_two_units_redirects_and_saves(
    live_server, credentials, mock_api
):
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 1,
        "items": [{"id": 1, "nm": "Unit #1"}],
    }
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
        expect(page).to_have_title("In-Progress Jobs | Terminus GPS")
        browser.close()
    assert InstallJob.objects.count() == 1
    assert WialonUnit.objects.get(imei="12345678912345678")
    assert WialonUnit.objects.get(imei="98765432198765432")


@pytest.mark.e2e
@pytest.mark.django_db
def test_new_job_form_reset_button(live_server, credentials, mock_api):
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 1,
        "items": [{"id": 1, "nm": "Unit #1"}],
    }
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
        page.get_by_role("button", name="Reset").click()
        expect(page).to_have_title("New Install Job | Terminus GPS")
        expect(page.get_by_label("Imei:")).to_have_value("")
        expect(page.get_by_label("Vin:")).to_have_value("")
        expect(page.get_by_label("Plate:")).to_have_value("")
        browser.close()
