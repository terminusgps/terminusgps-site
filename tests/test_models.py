from unittest import mock

from django.test import TestCase

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
