import pytest
from django.contrib.auth import get_user_model
from django.test import Client


@pytest.fixture
def client(credentials):
    client = Client()
    client.login(**credentials)
    return client


@pytest.fixture
def user(django_db_blocker, credentials):
    with django_db_blocker.unblock():
        user = get_user_model().objects.create_user(**credentials)
    yield user
    with django_db_blocker.unblock():
        user.delete()
