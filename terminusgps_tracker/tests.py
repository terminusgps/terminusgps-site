from uuid import uuid4

from django.test import TestCase

from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.items import (
    WialonResource,
    WialonUser,
    WialonUnit,
    WialonUnitGroup,
)


class WialonResourceTestCase(TestCase):
    def setUp(self) -> None:
        self.password: str = "SuperSecurePassword1!"
        self.test_id = str(uuid4())[:18]
        self.wialon_session = WialonSession().__enter__()
        self.terminus_1000 = WialonUser(id="27881459", session=self.wialon_session)

        self.test_super_user = WialonUser(
            owner=self.terminus_1000,
            name=f"super_test_user_{self.test_id}",
            password=self.password,
            session=self.wialon_session,
        )
        self.test_resource = WialonResource(
            owner=self.test_super_user,
            name=f"test_resource_{self.test_id}",
            session=self.wialon_session,
        )

    def tearDown(self) -> None:
        self.test_resource.delete()
        self.test_super_user.delete()
        self.wialon_session.__exit__(None, None, None)


class WialonUserTestCase(TestCase):
    def setUp(self) -> None:
        self.password: str = "Terminus#1"
        self.test_id = str(uuid4())[:18]
        self.wialon_session = WialonSession().__enter__()
        self.terminus_1000: WialonUser = WialonUser(
            id="27881459", session=self.wialon_session
        )

        self.test_super_user = WialonUser(
            owner=self.terminus_1000,
            name=f"super_test_user_{self.test_id}",
            password=self.password,
            session=self.wialon_session,
        )
        self.test_user = WialonUser(
            owner=self.test_super_user,
            name=f"test_user_{self.test_id}",
            password=self.password,
            session=self.wialon_session,
        )

    def tearDown(self) -> None:
        self.test_user.delete()
        self.test_super_user.delete()
        self.wialon_session.__exit__(None, None, None)


class WialonUnitGroupTestCase(TestCase):
    def setUp(self) -> None:
        self.password: str = "Terminus#1"
        self.test_id = str(uuid4())[:18]
        self.wialon_session = WialonSession().__enter__()
        self.terminus_1000: WialonUser = WialonUser(
            id="27881459", session=self.wialon_session
        )

        self.test_super_user = WialonUser(
            owner=self.terminus_1000,
            name=f"super_test_user_{self.test_id}",
            password=self.password,
            session=self.wialon_session,
        )
        self.test_user = WialonUser(
            owner=self.test_super_user,
            name=f"test_user_{self.test_id}",
            password=self.password,
            session=self.wialon_session,
        )
        self.test_group = WialonUnitGroup(
            owner=self.test_super_user,
            name=f"test_group_{self.test_id}",
            session=self.wialon_session,
        )

    def tearDown(self) -> None:
        self.test_group.delete()
        self.test_user.delete()
        self.test_super_user.delete()
        self.wialon_session.__exit__(None, None, None)

    def test_group_can_add_items(self) -> None:
        test_item_1 = WialonUnit(id="26691262", session=self.wialon_session)
        test_item_2 = WialonUnit(id="26691287", session=self.wialon_session)
        self.test_group.add_item(test_item_1)
        self.test_group.add_item(test_item_2)

        if (
            str(test_item_1.id) not in self.test_group.items
            or str(test_item_2.id) not in self.test_group.items
        ):
            self.fail(
                f"Failed to properly add test units to group. Test id: {self.test_id}"
            )

    def test_group_can_rm_items(self) -> None:
        test_item_1 = WialonUnit(id="26691262", session=self.wialon_session)
        test_item_2 = WialonUnit(id="26691287", session=self.wialon_session)
        self.test_group.add_item(test_item_1)
        self.test_group.add_item(test_item_2)
        self.test_group.rm_item(test_item_1)

        if (
            str(test_item_1.id) in self.test_group.items
            or str(test_item_2.id) not in self.test_group.items
        ):
            self.fail(
                f"Failed to properly remove a test unit from group. Test id: {self.test_id}"
            )


class WialonUnitTestCase(TestCase):
    def setUp(self) -> None:
        self.password: str = "Terminus#1"
        self.test_id = str(uuid4())[:18]
        self.wialon_session = WialonSession().__enter__()
        self.terminus_1000: WialonUser = WialonUser(
            id="27881459", session=self.wialon_session
        )
        self.test_unit: WialonUnit = WialonUnit(
            id="28675007", session=self.wialon_session
        )
        self.test_unit_old_name = "django_test_unit"

    def tearDown(self) -> None:
        self.test_unit.rename(self.test_unit_old_name)
        self.wialon_session.__exit__(None, None, None)

    def test_unit_can_be_renamed(self) -> None:
        new_name = f"test_unit_{self.test_id}"
        self.test_unit.rename(new_name)

        if (
            self.test_unit.name != new_name
            and self.test_unit.name == self.test_unit_old_name
        ):
            self.fail(f"Failed to properly rename test unit. Test id: {self.test_id}")
