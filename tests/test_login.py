import logging

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

logging.disable(logging.CRITICAL)


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def credentials():
    return {"username": "testuser", "password": "super_secure_password1!"}


@pytest.fixture(autouse=True)
def user(credentials):
    return get_user_model().objects.create_user(**credentials)


@pytest.mark.e2e
@pytest.mark.django_db
def test_login_view_success_redirects_to_home(live_server, credentials):
    """Fails if a successful login doesn't redirect the client to the homepage."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{live_server.url}{reverse('login')}")
        page.get_by_label("Username").fill(credentials["username"])
        page.get_by_label("Password").fill(credentials["password"])
        page.get_by_role("button", name="Login").click()
        expect(page).to_have_title("Home | Terminus GPS")
        browser.close()


@pytest.mark.e2e
@pytest.mark.django_db
def test_login_invalid_username_adds_error(live_server, credentials):
    """Fails if an invalid username doesn't add the expected form error."""
    expected_error_message = "Please enter a correct username and password. Note that both fields may be case-sensitive."
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{live_server.url}{reverse('login')}")
        page.get_by_label("Username").fill(credentials["username"][:-1])
        page.get_by_label("Password").fill(credentials["password"])
        page.get_by_role("button", name="Login").click()
        expect(page).to_have_title("Login | Terminus GPS")
        expect(page.get_by_text(expected_error_message)).to_have_count(1)
        browser.close()


@pytest.mark.e2e
@pytest.mark.django_db
def test_login_invalid_password_adds_error(live_server, credentials):
    """Fails if an invalid password doesn't add the expected form error."""
    expected_error_message = "Please enter a correct username and password. Note that both fields may be case-sensitive."
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{live_server.url}{reverse('login')}")
        page.get_by_label("Username").fill(credentials["username"])
        page.get_by_label("Password").fill(credentials["password"][:-1])
        page.get_by_role("button", name="Login").click()
        expect(page).to_have_title("Login | Terminus GPS")
        expect(page.get_by_text(expected_error_message)).to_have_count(1)
        browser.close()
