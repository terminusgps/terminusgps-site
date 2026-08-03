from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from terminusgps.wialon import WialonSession
from terminusgps_installer.models import (
    Employee,
    InstallJob,
    WialonResource,
    WialonUnit,
)
from terminusgps_site.models import ContactFormResponse


class ContactFormResponseTestCase(TestCase):
    def test_admin_email_message(self):
        """Fails if :py:attr:`admin_email_message` wasn't properly set."""
        contact_form_response = ContactFormResponse(
            name="test", email="test@domain.com", message="test"
        )
        contact_form_response.save()
        self.assertEqual(
            contact_form_response.admin_email_message,
            "Name: test\nEmail: test@domain.com\nMessage: test\n",
        )

    def test_admin_email_subject(self):
        """Fails if :py:attr:`admin_email_subject` wasn't properly set."""
        contact_form_response = ContactFormResponse(
            name="test", email="test@domain.com", message="test"
        )
        contact_form_response.save()
        self.assertEqual(
            contact_form_response.admin_email_subject,
            f"Contact Form Response - {str(contact_form_response)}",
        )

    def test_email_to_admins(self):
        """Fails if :py:meth:`email_to_admins` doesn't email the response to admins."""
        contact_form_response = ContactFormResponse(
            name="test", email="test@domain.com", message="test"
        )
        contact_form_response.save()
        with mock.patch(
            "terminusgps_site.models.mail_admins"
        ) as mock_mail_admins:
            contact_form_response.email_to_admins()
            mock_mail_admins.assert_called_once()


class WialonResourceTestCase(TestCase):
    fixtures = [
        "terminusgps/fixtures/terminusgps/tests/test_users.json",
        "terminusgps/fixtures/terminusgps/tests/test_employees.json",
        "terminusgps/fixtures/terminusgps/tests/test_installjobs.json",
        "terminusgps/fixtures/terminusgps/tests/test_wialonresources.json",
    ]

    def test_sync_from_wialon(self):
        """Fails if :py:meth:`sync_from_wialon` doesn't sync resources with an external Wialon API call."""
        with mock.patch(
            "terminusgps_installer.models.get_session",
            return_value=mock.MagicMock(WialonSession),
        ):
            with mock.patch(
                "terminusgps_installer.models.get_resources",
                return_value=[
                    {
                        "nm": "Test Resource #1",
                        "cls": 3,
                        "id": 1,
                        "mu": 1,
                        "uacl": 52913983520767,
                    }
                ],
            ):
                self.assertEqual(WialonResource.objects.count(), 237)
                WialonResource.objects.sync_from_wialon(sid=None)
                self.assertEqual(WialonResource.objects.count(), 238)
                new_resource = WialonResource.objects.get(pk=1)
                self.assertEqual(new_resource.name, "Test Resource #1")


class WialonUnitTestCase(TestCase):
    fixtures = [
        "terminusgps/fixtures/terminusgps/tests/test_users.json",
        "terminusgps/fixtures/terminusgps/tests/test_employees.json",
        "terminusgps/fixtures/terminusgps/tests/test_installjobs.json",
        "terminusgps/fixtures/terminusgps/tests/test_wialonresources.json",
        "terminusgps/fixtures/terminusgps/tests/test_wialonunits.json",
    ]

    def setUp(self):
        patcher = mock.patch(
            "terminusgps_installer.models.get_session",
            return_value=mock.MagicMock(WialonSession),
        )
        self.mock_get_session = patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_wialon_unit_name(self):
        """Fails if :py:meth:`_get_wialon_unit_name` doesn't return a unit name from the Wialon API."""
        expected_name = "test name"
        test_unit = WialonUnit.objects.first()
        with mock.patch(
            "terminusgps_installer.models.get_unit_by_imei",
            return_value={"nm": expected_name},
        ):
            result = test_unit._get_wialon_unit_name(sid=None)
            self.assertEqual(result, expected_name)

    def test_get_wialon_unit_id(self):
        """Fails if :py:meth:`_get_wialon_unit_id` doesn't return a unit id from the Wialon API."""
        expected_id = 1
        test_unit = WialonUnit.objects.first()
        with mock.patch(
            "terminusgps_installer.models.get_unit_by_imei",
            return_value={"id": expected_id},
        ):
            result = test_unit._get_wialon_unit_id(sid=None)
            self.assertEqual(result, expected_id)

    def test_get_wialon_commands(self):
        """Fails if :py:meth:`_get_wialon_commands` doesn't return a list of commands from the Wialon API."""
        expected_commands = [
            {
                "n": "Disable Ignition",
                "a": 1,
                "t": "tcp,vrt",
                "c": "custom_msg",
                "p": "relay,1#",
                "jp": "",
            },
            {
                "n": "Enable Ignition",
                "a": 1,
                "t": "tcp,vrt",
                "c": "custom_msg",
                "p": "relay,0#",
                "jp": "",
            },
        ]
        test_unit = WialonUnit.objects.first()
        with mock.patch(
            "terminusgps_installer.models.get_unit_by_imei",
            return_value={"cmds": expected_commands},
        ):
            result = test_unit._get_wialon_commands(sid=None)
            self.assertEqual(result, expected_commands)

    def test_get_wialon_unit_name_and_save(self):
        """Fails if :py:meth:`get_wialon_unit_name_and_save` doesn't retrieve the unit's name from Wialon and save it."""
        expected_name = "Test Unit Name"
        test_unit = WialonUnit.objects.first()
        with mock.patch(
            "terminusgps_installer.models.get_unit_by_imei",
            return_value={"nm": expected_name},
        ):
            self.assertEqual(test_unit.name, "")
            test_unit.get_wialon_unit_name_and_save()
            self.assertEqual(test_unit.name, expected_name)

    def test_refresh_locator_url_and_save(self):
        """Fails if :py:meth:`refresh_locator_url_and_save` doesn't refresh the unit's :py:attr:`locator_url` and save it."""
        expected_url = "http://localhost:8000/locator/"
        test_unit = WialonUnit.objects.first()
        with mock.patch(
            "terminusgps_installer.models.get_unit_by_imei",
            return_value={"id": 1},
        ):
            with mock.patch(
                "terminusgps_installer.models.generate_locator_token",
                return_value="super_secure_token",
            ):
                with mock.patch(
                    "terminusgps_installer.models.generate_locator_url",
                    return_value=expected_url,
                ):
                    self.assertEqual(test_unit.locator_url, "")
                    test_unit.refresh_locator_url_and_save()
                    self.assertEqual(test_unit.locator_url, expected_url)

    def test_with_wialon_commands(self):
        """Fails if :py:meth:`with_wialon_commands` doesn't return a list of tuples containing a WialonUnit and its commands from the Wialon API."""
        expected_commands = [
            {
                "n": "Disable Ignition",
                "a": 1,
                "t": "tcp,vrt",
                "c": "custom_msg",
                "p": "relay,1#",
                "jp": "",
            },
            {
                "n": "Enable Ignition",
                "a": 1,
                "t": "tcp,vrt",
                "c": "custom_msg",
                "p": "relay,0#",
                "jp": "",
            },
        ]

        with mock.patch(
            "terminusgps_installer.models.get_unit_by_imei",
            return_value={"cmds": expected_commands},
        ):
            result = WialonUnit.objects.filter().with_wialon_commands()
            self.assertEqual(result[0][0], WialonUnit.objects.get(pk=1))
            self.assertEqual(result[0][1], expected_commands)
            self.assertEqual(result[1][0], WialonUnit.objects.get(pk=2))
            self.assertEqual(result[1][1], expected_commands)

    def test___str__(self):
        """Fails if :py:meth:`__str__` returns unexpected values."""
        test_unit = WialonUnit.objects.first()
        self.assertEqual(test_unit.name, "")
        self.assertEqual(str(test_unit), "WialonUnit #1")
        test_unit.name = "Test Unit"
        test_unit.save(update_fields=["name"])
        self.assertEqual(test_unit.name, "Test Unit")
        self.assertEqual(str(test_unit), "Test Unit")


class EmployeeTestCase(TestCase):
    fixtures = [
        "terminusgps/fixtures/terminusgps/tests/test_users.json",
        "terminusgps/fixtures/terminusgps/tests/test_employees.json",
    ]

    def test_get_by_user_returns_employee(self):
        """Fails if :py:meth:`get_by_user` doesn't return the expected employee."""
        test_user = get_user_model().objects.get(pk=1)
        result = Employee.objects.get_by_user(test_user)
        self.assertEqual(result, Employee.objects.get(pk=1))

    def test_get_by_user_returns_none(self):
        """Fails if :py:meth:`get_by_user` doesn't return :py:obj:`None` if there was no associated Employee."""
        test_user = get_user_model().objects.get(pk=1)
        employee = Employee.objects.get_by_user(test_user)
        employee.delete()
        result = Employee.objects.get_by_user(test_user)
        self.assertIsNone(result)


class InstallJobTestCase(TestCase):
    fixtures = [
        "terminusgps/fixtures/terminusgps/tests/test_employees.json",
        "terminusgps/fixtures/terminusgps/tests/test_installjobs.json",
        "terminusgps/fixtures/terminusgps/tests/test_users.json",
        "terminusgps/fixtures/terminusgps/tests/test_wialonresources.json",
        "terminusgps/fixtures/terminusgps/tests/test_wialonunits.json",
    ]

    def test_all_not_done_jobs(self):
        """Fails if :py:meth:`all_not_done_jobs` returns jobs with status ``done``."""
        expected_qs = InstallJob.objects.exclude(status="done")
        result = InstallJob.objects.all_not_done_jobs()
        self.assertQuerySetEqual(result, expected_qs)

    def test___str__(self):
        """Fails if :py:meth:`__str__` returns unexpected values."""
        test_job = InstallJob.objects.first()
        self.assertEqual(str(test_job), "InstallJob #1")
