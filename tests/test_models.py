from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model

from terminusgps_installer.models import (
    Employee,
    InstallJob,
    InstallJobStatus,
    WialonResource,
    WialonUnit,
)


@pytest.fixture
def mock_api():
    with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
        mock_api = MagicMock()
        mock_api.token_login.return_value = {
            "eid": "abc123",
            "au": "test",
            "user": {"id": 1},
            "gis_sid": "def456",
        }
        mock_wialon_cls.return_value = mock_api
        yield mock_api


@pytest.fixture(autouse=True)
def user(db):
    return get_user_model().objects.create_user(
        username="testuser", password="super_secure_password1!"
    )


@pytest.fixture(autouse=True)
def employee(user):
    return Employee.objects.create(user=user)


@pytest.fixture(autouse=True)
def resource(db):
    return WialonResource.objects.create(id=1, name="Resource #1")


@pytest.fixture
def install_jobs(employee, resource):
    jobs = [
        InstallJob(
            id=1,
            company=resource,
            employee=employee,
            status=InstallJobStatus.DONE,
        ),
        InstallJob(
            id=2,
            company=resource,
            employee=employee,
            status=InstallJobStatus.NEEDS_BILLING,
        ),
    ]
    InstallJob.objects.bulk_create(jobs, ignore_conflicts=True)
    return jobs


@pytest.mark.django_db
def test_installjob_all_not_done_jobs(install_jobs):
    assert set(InstallJob.objects.all_not_done_jobs()) == set(
        InstallJob.objects.exclude(status=InstallJobStatus.DONE)
    )


@pytest.mark.django_db
def test_installjob_str(install_jobs):
    assert str(install_jobs[0]) == "InstallJob #1"
    assert str(install_jobs[1]) == "InstallJob #2"


@pytest.mark.django_db
def test_employee_str(employee):
    assert str(employee) == "testuser"


@pytest.mark.django_db
def test_wialonunit_str(install_jobs):
    unit = WialonUnit.objects.create(id=1, job=install_jobs[0], imei="abc")
    assert str(unit) == "WialonUnit #1"
    unit.name = "New Name"
    unit.save(update_fields=["name"])
    assert str(unit) == "New Name"


@pytest.mark.django_db
def test_wialonresource_str(resource):
    assert str(resource) == "Resource #1"


@pytest.mark.django_db
def test_employeequeryset_get_by_user():
    user_0 = get_user_model().objects.create_user(
        username="testuser0", password="super_secure_password1!"
    )
    employee_0 = Employee.objects.create(user=user_0)
    user_1 = get_user_model().objects.create_user(
        username="testuser1", password="super_secure_password1!"
    )
    assert employee_0 == Employee.objects.get_by_user(user_0)
    assert Employee.objects.get_by_user(user_1) is None


@pytest.mark.django_db
def test_wialonresourcequeryset_sync_from_wialon(mock_api):
    assert WialonResource.objects.count() == 1
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 2,
        "items": [
            {"id": 1, "nm": "Resource #1"},
            {"id": 2, "nm": "Resource #2"},
        ],
    }
    WialonResource.objects.sync_from_wialon(sid=None)
    assert WialonResource.objects.count() == 2


@pytest.mark.django_db
def test_wialonunitqueryset_with_wialon_commands(mock_api, install_jobs):
    WialonUnit.objects.create(job=install_jobs[0], imei="abc")
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 1,
        "items": [
            {
                "id": 1,
                "nm": "Unit #1",
                "cmds": [
                    {
                        "n": "Ignition On",
                        "a": 1,
                        "t": "vrt",
                        "c": "custom_msg",
                    },
                    {
                        "n": "Ignition Off",
                        "a": 1,
                        "t": "vrt",
                        "c": "custom_msg",
                    },
                    {
                        "n": "Location Query",
                        "a": 1,
                        "t": "vrt",
                        "c": "custom_msg",
                    },
                ],
            }
        ],
    }
    result = WialonUnit.objects.with_wialon_commands()
    unit, commands = result[0][0], result[0][1]
    assert unit.pk == 1
    assert len(commands) == 3
    assert commands[0]["n"] == "Ignition On"
    assert commands[1]["n"] == "Ignition Off"
    assert commands[2]["n"] == "Location Query"


@pytest.mark.django_db
def test_wialonunit_get_wialon_unit_name_and_save(mock_api, install_jobs):
    unit = WialonUnit.objects.create(
        job=install_jobs[0], imei="abc", name="Old Name"
    )
    assert unit.name == "Old Name"
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 1,
        "items": [{"id": 1, "nm": "New Name"}],
    }
    unit.get_wialon_unit_name_and_save()
    assert unit.name == "New Name"


@pytest.mark.django_db
def test_wialonunit_refresh_locator_url(mock_api, install_jobs):
    unit = WialonUnit.objects.create(job=install_jobs[0], imei="abc")
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 1,
        "items": [{"id": 12345678, "nm": "New Name"}],
    }
    mock_api.token_update.return_value = {"h": "locator_token"}
    unit.refresh_locator_url_and_save()
    assert (
        unit.locator_url
        == "https://hosting.terminusgps.com/locator/index.html?t=locator_token"
    )
