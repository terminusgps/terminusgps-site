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
        self.test_session = session_manager.get_session(log_level=logging.DEBUG)
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
        print("TrackerProfileTestCase.setUp() complete...")
        print(f"Called Wialon API {self.test_session.wialon_api.num_calls} times.")

    def tearDown(self) -> None:
        self.test_resource.delete()
        self.test_session.logout()
        print("TrackerProfileTestCase.tearDown() complete...")

    def test_wialon_unit_can_be_migrated(self) -> None:
        try:
            self.test_resource.migrate_unit(unit=self.test_unit)
        except WialonError as e:
            self.fail(e)
