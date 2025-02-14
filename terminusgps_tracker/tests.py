import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.utils import timezone
from wialon.api import WialonError

from terminusgps.wialon import constants, flags
from terminusgps.wialon.session import WialonSessionManager
from terminusgps.wialon.utils import generate_wialon_password, get_hw_type_id
from terminusgps.wialon.items import (
    WialonResource,
    WialonUnit,
    WialonUser,
    WialonUnitGroup,
)

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

        # Create test objects
        self.test_unit = WialonUnit(
            id=None,
            session=self.test_session,
            creator_id=settings.WIALON_ADMIN_ID,
            name=f"test_unit_{self.test_timestamp}",
            hw_type_id=get_hw_type_id("Test HW", self.test_session),
        )
        self.test_super_user = WialonUser(
            id=None,
            session=self.test_session,
            creator_id=settings.WIALON_ADMIN_ID,
            name=f"test_super_user_{self.test_timestamp}",
            password=generate_wialon_password(),
        )
        self.test_resource = WialonResource(
            id=None,
            session=self.test_session,
            creator_id=self.test_super_user.id,
            name=f"test_account_{self.test_timestamp}",
        )
        self.test_end_user = WialonUser(
            id=None,
            session=self.test_session,
            creator_id=self.test_super_user.id,
            name=f"test_end_user_{self.test_timestamp}",
            password=generate_wialon_password(),
        )
        self.test_unit_group = WialonUnitGroup(
            id=None,
            session=self.test_session,
            creator_id=self.test_super_user.id,
            name=f"test_group_{self.test_timestamp}",
        )

        self.test_super_user.grant_access(
            self.test_unit, access_mask=constants.ACCESSMASK_UNIT_MIGRATION
        )
        self.test_end_user.grant_access(
            self.test_unit_group, access_mask=constants.ACCESSMASK_UNIT_BASIC
        )
        self.test_end_user.grant_access(
            self.test_resource, access_mask=constants.ACCESSMASK_RESOURCE_BASIC
        )

        # Create the test account
        self.test_resource.create_account("terminusgps_ext_hist")
        self.test_resource.enable_account()

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
            self.test_resource.set_settings_flags()
            self.test_resource.add_days(30)
        except (WialonError, ValueError) as e:
            self.fail(e)

    def test_wialon_account_can_set_minimum_days(self) -> None:
        """Fails if minimum days cannot be set on the test account."""
        try:
            self.test_resource.set_settings_flags()
            self.test_resource.add_days(30)
            self.test_resource.set_minimum_days(0)
        except (WialonError, ValueError) as e:
            self.fail(e)
