from django.test import TestCase

from terminusgps_installer.models import InstallJob, InstallJobStatus


class InstallJobQuerySetTestCase(TestCase):
    fixtures = [
        "terminusgps_installer/tests/test_users.json",
        "terminusgps_installer/tests/test_employees.json",
        "terminusgps_installer/tests/test_jobs.json",
    ]

    def test_all_not_done_jobs(self):
        """Fails if :py:meth:`all_not_done_jobs` returns any done jobs."""
        expected = InstallJob.objects.exclude(status=InstallJobStatus.DONE)
        result = InstallJob.objects.all_not_done_jobs()
        self.assertQuerySetEqual(expected, result)
