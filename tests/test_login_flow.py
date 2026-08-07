import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_login_view_success_redirects_to_home(live_server):
    """Fails if a successful login doesn't redirect the client to the homepage."""
    username = "testuser"
    password = "super_secure_password1!"
    get_user_model().objects.create_user(username=username, password=password)
    p = sync_playwright().start()
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"{live_server.url}{reverse('login')}")
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_title("Home | Terminus GPS")
    browser.close()
    p.stop()


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_login_invalid_username_adds_error(live_server):
    """Fails if an invalid username doesn't add the expected form error."""
    expected_error_message = "Please enter a correct username and password. Note that both fields may be case-sensitive."
    username = "testuser"
    password = "super_secure_password1!"
    get_user_model().objects.create_user(username=username, password=password)
    p = sync_playwright().start()
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"{live_server.url}{reverse('login')}")
    page.get_by_label("Username").fill("testuse")
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_title("Login | Terminus GPS")
    expect(page.get_by_text(expected_error_message)).to_have_count(1)
    browser.close()
    p.stop()


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_login_invalid_password_adds_error(live_server):
    """Fails if an invalid password doesn't add the expected form error."""
    expected_error_message = "Please enter a correct username and password. Note that both fields may be case-sensitive."
    username = "testuser"
    password = "super_secure_password1!"
    get_user_model().objects.create_user(username=username, password=password)
    p = sync_playwright().start()
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"{live_server.url}{reverse('login')}")
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password").fill("super_secure_password1")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_title("Login | Terminus GPS")
    expect(page.get_by_text(expected_error_message)).to_have_count(1)
    browser.close()
    p.stop()
