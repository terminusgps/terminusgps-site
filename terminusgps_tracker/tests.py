import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.utils import timezone
from terminusgps.wialon.items import WialonResource, WialonUnit, WialonUser
from terminusgps.wialon.session import WialonSessionManager
from terminusgps.wialon.utils import gen_wialon_password, get_hw_type_id
from terminusgps.wialon import constants
from wialon.api import WialonError

session_manager = WialonSessionManager()

if not hasattr(settings, "WIALON_ADMIN_ID"):
    raise ImproperlyConfigured("'WIALON_ADMIN_ID' setting is required.")
if not hasattr(settings, "WIALON_DEFAULT_PLAN"):
    raise ImproperlyConfigured("'WIALON_DEFAULT_PLAN' setting is required.")


class TrackerProfileTestCase(TestCase):
    def setUp(self) -> None:
        # Create common variables
        self.test_timestamp = f"{timezone.now():%Y_%m_%d_%H:%M:%S}"
        self.test_billing_plan = settings.WIALON_DEFAULT_PLAN
        self.test_session = session_manager.get_session(log_level=logging.INFO)
        self.test_session.login(self.test_session.token)

        # Create common Wialon objects
        self.test_unit = WialonUnit(
            creator_id=settings.WIALON_ADMIN_ID,
            name=f"test_unit_{self.test_timestamp}",
            hw_type_id=get_hw_type_id("Test HW", self.test_session),
            session=self.test_session,
        )
        self.test_super_user = WialonUser(
            creator_id=settings.WIALON_ADMIN_ID,
            name=f"test_user_{self.test_timestamp}",
            password=gen_wialon_password(32),
            session=self.test_session,
        )
        self.test_resource = WialonResource(
            creator_id=self.test_super_user.id,
            name=f"test_resource_{self.test_timestamp}",
            session=self.test_session,
        )

        # Grant permissions and create test account
        self.test_super_user.grant_access(
            self.test_unit, access_mask=constants.ACCESSMASK_UNIT_MIGRATION
        )
        self.test_super_user.grant_access(
            self.test_resource, access_mask=constants.ACCESSMASK_UNIT_FULL
        )
        self.test_resource.create_account(billing_plan=self.test_billing_plan)
        self.test_resource.enable_account()
        self.test_resource.set_settings_flags()

    def tearDown(self) -> None:
        # self.test_resource.delete()
        self.test_session.logout()

    def test_wialon_account_can_migrate_unit(self) -> None:
        """Fails if a Wialon unit cannot be migrated into the test account."""
        try:
            self.test_resource.migrate_unit(unit=self.test_unit)
        except (WialonError, ValueError) as e:
            self.fail(e)

    def test_wialon_account_can_add_days(self) -> None:
        """Fails if days cannot be added to the test account."""
        try:
            self.test_resource.add_days(30)
        except (WialonError, ValueError) as e:
            self.fail(e)

    def test_wialon_account_can_set_minimum_days(self) -> None:
        """Fails if minimum days cannot be set on the test account."""
        try:
            self.test_resource.set_minimum_days(0)
        except (WialonError, ValueError) as e:
            self.fail(e)
