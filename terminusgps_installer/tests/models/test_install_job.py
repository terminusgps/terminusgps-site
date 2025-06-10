from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from terminusgps.wialon.items import WialonResource, WialonUnit
from terminusgps.wialon.session import WialonSession

from terminusgps_installer.models import Installer, WialonAccount, WialonAsset


class InstallJobTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = get_user_model().objects.create_user(
            first_name="Test",
            last_name="User",
            username="test_user@domain.com",
            email="test_user@domain.com",
            password="test_user_password1!",
        )
        cls.test_installer = Installer.objects.create(user=cls.test_user)
        with WialonSession() as session:
            resource = WialonResource(
                creator_id=str(settings.WIALON_ADMIN_ID),
                name=f"{cls.test_user.username}_account",
                skip_creator_check=True,
                session=session,
            )
            resource.create_account("terminusgps_ext_hist")
            resource.enable_account()
            unit = WialonUnit(
                creator_id=str(settings.WIALON_ADMIN_ID),
                name=f"{cls.test_user.username}_asset",
                hw_type_id="Test HW",
                session=session,
            )

            cls.test_account = WialonAccount.objects.create(
                id=resource.id, name=resource.name
            )
            cls.test_asset = WialonAsset.objects.create(
                id=unit.id, name=unit.name, imei=unit.imei_number
            )

    def tearDown(self) -> None:
        with WialonSession() as session:
            resource = WialonResource(id=self.test_account.pk, session=session)
            unit = WialonUnit(id=self.test_asset.pk, session=session)
            resource.delete_account()
            unit.delete()
        self.test_user.delete()
