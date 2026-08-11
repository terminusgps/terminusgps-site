from unittest.mock import MagicMock

import pytest
from django.test import Client

import terminusgps.wialon


@pytest.fixture
def mock_api(monkeypatch):
    mock_api = MagicMock()
    mock_api.token_login.return_value = {
        "eid": "abc123",
        "au": "test",
        "user": {"id": 1},
        "gis_sid": "def456",
    }
    mock_wialon_cls = MagicMock(return_value=mock_api)
    monkeypatch.setattr(terminusgps.wialon, "Wialon", mock_wialon_cls)
    yield mock_api


@pytest.fixture
def client():
    return Client()


@pytest.fixture(autouse=True, scope="session")
def credentials():
    return {"username": "testuser", "password": "super_secure_password1!"}
